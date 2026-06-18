output "state_machine_arn" {
  value = aws_sfn_state_machine.conversion.arn
}

output "state_machine_name" {
  value = aws_sfn_state_machine.conversion.name
}

output "step_functions_log_group_name" {
  value = aws_cloudwatch_log_group.conversion.name
}

