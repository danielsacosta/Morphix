output "api_endpoint" {
  value = length(aws_apigatewayv2_api.api) > 0 ? aws_apigatewayv2_api.api[0].api_endpoint : ""
}

output "api_log_group_name" {
  value = aws_cloudwatch_log_group.api.name
}

output "api_lambda_name" {
  value = length(aws_lambda_function.api) > 0 ? aws_lambda_function.api[0].function_name : ""
}

output "websocket_endpoint" {
  value = length(aws_apigatewayv2_api.websocket) > 0 ? "wss://${aws_apigatewayv2_api.websocket[0].id}.execute-api.${var.aws_region}.amazonaws.com/${aws_apigatewayv2_stage.websocket[0].name}" : ""
}

output "websocket_connections_table_name" {
  value = aws_dynamodb_table.websocket_connections.name
}

output "state_machine_arn" {
  value = aws_sfn_state_machine.conversion.arn
}

output "state_machine_name" {
  value = aws_sfn_state_machine.conversion.name
}

output "step_functions_log_group_name" {
  value = aws_cloudwatch_log_group.conversion.name
}
