locals {
  name                              = "${var.project_name}-${var.environment}"
  create_runtime                    = var.api_package_path != ""
  log_group                         = "/aws/lambda/${local.name}-api"
  state_machine_log_group           = "/aws/stepfunctions/${local.name}-conversion"
  state_machine_definition_template = file(var.state_machine_definition_path)
  state_machine_definition = replace(
    replace(
      replace(
        replace(
          replace(
            local.state_machine_definition_template,
            "\"__JOBS_TABLE_NAME__\"",
            jsonencode(var.jobs_table_name)
          ),
          "\"__CLUSTER_ARN__\"",
          jsonencode(var.cluster_arn)
        ),
        "\"__TASK_DEFINITION_ARN__\"",
        jsonencode(var.task_definition_arn)
      ),
      "\"__WORKER_SECURITY_GROUP_IDS__\"",
      jsonencode([var.worker_security_group_id])
    ),
    "\"__PRIVATE_SUBNET_IDS__\"",
    jsonencode(var.private_subnet_ids)
  )
}

data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

resource "aws_cloudwatch_log_group" "api" {
  name              = local.log_group
  retention_in_days = 14
  tags              = var.tags
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "api" {
  name               = "${local.name}-api"
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.api.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "api" {
  statement {
    sid       = "JobsTableAccess"
    actions   = ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:Query"]
    resources = [var.jobs_table_arn, "${var.jobs_table_arn}/index/*"]
  }

  statement {
    sid       = "PresignedInputOutput"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${var.input_bucket_arn}/*", "${var.output_bucket_arn}/*"]
  }

  statement {
    sid       = "StartConversions"
    actions   = ["states:StartExecution"]
    resources = [aws_sfn_state_machine.conversion.arn]
  }
}

resource "aws_iam_role_policy" "api" {
  name   = "${local.name}-api-policy"
  role   = aws_iam_role.api.id
  policy = data.aws_iam_policy_document.api.json
}

resource "aws_lambda_function" "api" {
  count = local.create_runtime ? 1 : 0

  function_name    = "${local.name}-api"
  role             = aws_iam_role.api.arn
  package_type     = "Zip"
  filename         = var.api_package_path
  source_code_hash = filebase64sha256(var.api_package_path)
  runtime          = "python3.11"
  handler          = "morphix_api.main.handler"
  architectures    = ["x86_64"]
  timeout          = 30
  memory_size      = 512

  environment {
    variables = {
      PROJECT_NAME      = var.project_name
      ENVIRONMENT       = var.environment
      AWS_REGION        = var.aws_region
      JOBS_TABLE_NAME   = var.jobs_table_name
      INPUT_BUCKET      = var.input_bucket_name
      OUTPUT_BUCKET     = var.output_bucket_name
      STATE_MACHINE_ARN = aws_sfn_state_machine.conversion.arn
      MAX_FILE_SIZE_MB  = tostring(var.max_file_size_mb)
      ALLOWED_ORIGINS   = join(",", var.allowed_origins)
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.api,
    aws_iam_role_policy_attachment.basic,
    aws_iam_role_policy.api
  ]

  tags = var.tags
}

resource "aws_apigatewayv2_api" "api" {
  count = local.create_runtime ? 1 : 0

  name          = "${local.name}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_headers = ["Content-Type", "X-User-Id"]
    allow_methods = ["GET", "POST", "DELETE", "OPTIONS"]
    allow_origins = var.allowed_origins
    max_age       = 900
  }

  tags = var.tags
}

resource "aws_apigatewayv2_integration" "lambda" {
  count = local.create_runtime ? 1 : 0

  api_id                 = aws_apigatewayv2_api.api[0].id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api[0].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  count = local.create_runtime ? 1 : 0

  api_id    = aws_apigatewayv2_api.api[0].id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda[0].id}"
}

resource "aws_apigatewayv2_stage" "default" {
  count = local.create_runtime ? 1 : 0

  api_id      = aws_apigatewayv2_api.api[0].id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 50
    throttling_rate_limit  = 25
  }

  tags = var.tags
}

resource "aws_lambda_permission" "api_gateway" {
  count = local.create_runtime ? 1 : 0

  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api[0].execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "conversion" {
  name              = local.state_machine_log_group
  retention_in_days = 14
  tags              = var.tags
}

data "aws_iam_policy_document" "states_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "state_machine" {
  name               = "${local.name}-conversion-sfn"
  assume_role_policy = data.aws_iam_policy_document.states_assume.json
  tags               = var.tags
}

data "aws_iam_policy_document" "state_machine" {
  statement {
    sid       = "RunWorkerTask"
    actions   = ["ecs:RunTask", "ecs:StopTask", "ecs:DescribeTasks"]
    resources = ["*"]
  }

  statement {
    sid       = "ManageEcsSyncEventsRule"
    actions   = ["events:PutRule", "events:PutTargets", "events:DescribeRule"]
    resources = ["arn:${data.aws_partition.current.partition}:events:${var.aws_region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForECSTaskRule"]
  }

  statement {
    sid       = "PassWorkerRoles"
    actions   = ["iam:PassRole"]
    resources = [var.task_execution_role_arn, var.task_role_arn]
  }

  statement {
    sid       = "UpdateJobStatus"
    actions   = ["dynamodb:UpdateItem"]
    resources = [var.jobs_table_arn]
  }

  statement {
    sid = "WriteExecutionLogs"
    actions = [
      "logs:CreateLogDelivery",
      "logs:GetLogDelivery",
      "logs:UpdateLogDelivery",
      "logs:DeleteLogDelivery",
      "logs:ListLogDeliveries",
      "logs:PutResourcePolicy",
      "logs:DescribeResourcePolicies",
      "logs:DescribeLogGroups"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "state_machine" {
  name   = "${local.name}-conversion-sfn-policy"
  role   = aws_iam_role.state_machine.id
  policy = data.aws_iam_policy_document.state_machine.json
}

resource "aws_sfn_state_machine" "conversion" {
  name       = "${local.name}-conversion"
  role_arn   = aws_iam_role.state_machine.arn
  type       = "STANDARD"
  definition = local.state_machine_definition

  logging_configuration {
    include_execution_data = false
    level                  = "ERROR"
    log_destination        = "${aws_cloudwatch_log_group.conversion.arn}:*"
  }

  depends_on = [aws_iam_role_policy.state_machine]

  tags = var.tags
}
