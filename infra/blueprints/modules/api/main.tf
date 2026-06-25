locals {
  name                              = "${var.project_name}-${var.environment}"
  create_runtime                    = var.api_package_path != ""
  log_group                         = "/aws/lambda/${local.name}-api"
  websocket_log_group               = "/aws/lambda/${local.name}-websocket"
  broadcaster_log_group             = "/aws/lambda/${local.name}-realtime-broadcaster"
  state_machine_log_group           = "/aws/stepfunctions/${local.name}-conversion"
  jobs_table_stream_policy_arn      = var.jobs_table_stream_arn != "" ? var.jobs_table_stream_arn : "${var.jobs_table_arn}/stream/*"
  state_machine_definition_template = file(var.state_machine_definition_path)
  state_machine_definition = replace(
    replace(
      replace(
        local.state_machine_definition_template,
        "\"__JOBS_TABLE_NAME__\"",
        jsonencode(var.jobs_table_name)
      ),
      "\"__CONVERSION_QUEUE_URL__\"",
      jsonencode(var.conversion_queue_url)
    ),
    "\"__WORKER_CALLBACK_TIMEOUT_SECONDS__\"",
    tostring(var.worker_callback_timeout_seconds)
  )
}

resource "aws_cloudwatch_log_group" "api" {
  name              = local.log_group
  retention_in_days = 14
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "websocket" {
  name              = local.websocket_log_group
  retention_in_days = 14
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "broadcaster" {
  name              = local.broadcaster_log_group
  retention_in_days = 14
  tags              = var.tags
}

resource "aws_dynamodb_table" "websocket_connections" {
  name         = "${local.name}-websocket-connections"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "connection_id"

  attribute {
    name = "connection_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name            = "user_id-index"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = merge(var.tags, {
    Name = "${local.name}-websocket-connections"
  })
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

data "aws_caller_identity" "current" {}

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
    sid = "WebSocketConnectionsTableAccess"
    actions = [
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query"
    ]
    resources = [
      aws_dynamodb_table.websocket_connections.arn,
      "${aws_dynamodb_table.websocket_connections.arn}/index/*"
    ]
  }

  statement {
    sid = "ReadJobsStream"
    actions = [
      "dynamodb:DescribeStream",
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:ListStreams"
    ]
    resources = [local.jobs_table_stream_policy_arn]
  }

  statement {
    sid       = "ManageWebSocketConnections"
    actions   = ["execute-api:ManageConnections"]
    resources = ["arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*/*/POST/@connections/*"]
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

resource "aws_lambda_function" "websocket_connections" {
  count = local.create_runtime ? 1 : 0

  function_name    = "${local.name}-websocket"
  role             = aws_iam_role.api.arn
  package_type     = "Zip"
  filename         = var.api_package_path
  source_code_hash = filebase64sha256(var.api_package_path)
  runtime          = "python3.11"
  handler          = "morphix_api.realtime.connection_handler.handler"
  architectures    = ["x86_64"]
  timeout          = 10
  memory_size      = 256

  environment {
    variables = {
      CONNECTIONS_TABLE_NAME = aws_dynamodb_table.websocket_connections.name
      CONNECTION_TTL_SECONDS = tostring(var.websocket_connection_ttl_seconds)
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.websocket,
    aws_iam_role_policy_attachment.basic,
    aws_iam_role_policy.api
  ]

  tags = var.tags
}

resource "aws_lambda_function" "realtime_broadcaster" {
  count = local.create_runtime ? 1 : 0

  function_name    = "${local.name}-realtime-broadcaster"
  role             = aws_iam_role.api.arn
  package_type     = "Zip"
  filename         = var.api_package_path
  source_code_hash = filebase64sha256(var.api_package_path)
  runtime          = "python3.11"
  handler          = "morphix_api.realtime.broadcaster.handler"
  architectures    = ["x86_64"]
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      CONNECTIONS_TABLE_NAME = aws_dynamodb_table.websocket_connections.name
      WEBSOCKET_API_ENDPOINT = local.create_runtime ? "https://${aws_apigatewayv2_api.websocket[0].id}.execute-api.${var.aws_region}.amazonaws.com/${aws_apigatewayv2_stage.websocket[0].name}" : ""
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.broadcaster,
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

resource "aws_apigatewayv2_api" "websocket" {
  count = local.create_runtime ? 1 : 0

  name                       = "${local.name}-websocket"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"

  tags = var.tags
}

resource "aws_apigatewayv2_integration" "websocket_connections" {
  count = local.create_runtime ? 1 : 0

  api_id                 = aws_apigatewayv2_api.websocket[0].id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.websocket_connections[0].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "websocket_connect" {
  count = local.create_runtime ? 1 : 0

  api_id    = aws_apigatewayv2_api.websocket[0].id
  route_key = "$connect"
  target    = "integrations/${aws_apigatewayv2_integration.websocket_connections[0].id}"
}

resource "aws_apigatewayv2_route" "websocket_disconnect" {
  count = local.create_runtime ? 1 : 0

  api_id    = aws_apigatewayv2_api.websocket[0].id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.websocket_connections[0].id}"
}

resource "aws_apigatewayv2_stage" "websocket" {
  count = local.create_runtime ? 1 : 0

  api_id      = aws_apigatewayv2_api.websocket[0].id
  name        = var.environment
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 100
    throttling_rate_limit  = 50
  }

  tags = var.tags
}

resource "aws_lambda_permission" "websocket_api_gateway" {
  count = local.create_runtime ? 1 : 0

  statement_id  = "AllowWebSocketApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.websocket_connections[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket[0].execution_arn}/*/*"
}

resource "aws_lambda_event_source_mapping" "jobs_stream_broadcaster" {
  count = local.create_runtime && var.jobs_table_stream_arn != "" ? 1 : 0

  event_source_arn  = var.jobs_table_stream_arn
  function_name     = aws_lambda_function.realtime_broadcaster[0].arn
  starting_position = "LATEST"
  batch_size        = 25
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
    sid       = "UpdateJobStatus"
    actions   = ["dynamodb:UpdateItem"]
    resources = [var.jobs_table_arn]
  }

  statement {
    sid       = "EnqueueWorker"
    actions   = ["sqs:SendMessage"]
    resources = [var.conversion_queue_arn]
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
