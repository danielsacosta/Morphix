locals {
  name           = "${var.project_name}-${var.environment}"
  create_runtime = var.api_package_path != ""
  log_group      = "/aws/lambda/${local.name}-api"
}

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
    resources = [var.state_machine_arn]
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
      STATE_MACHINE_ARN = var.state_machine_arn
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
