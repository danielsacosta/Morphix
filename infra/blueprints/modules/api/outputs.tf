output "api_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "api_endpoint" {
  value = length(aws_apigatewayv2_api.api) > 0 ? aws_apigatewayv2_api.api[0].api_endpoint : ""
}

output "api_log_group_name" {
  value = aws_cloudwatch_log_group.api.name
}

output "api_lambda_name" {
  value = length(aws_lambda_function.api) > 0 ? aws_lambda_function.api[0].function_name : ""
}
