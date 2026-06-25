output "dashboard_name" {
  value = aws_cloudwatch_dashboard.main.dashboard_name
}

output "worker_failures_alarm_name" {
  value = aws_cloudwatch_metric_alarm.worker_failures.alarm_name
}

output "step_functions_failed_alarm_name" {
  value = aws_cloudwatch_metric_alarm.step_functions_failed.alarm_name
}

output "conversion_dlq_alarm_name" {
  value = aws_cloudwatch_metric_alarm.conversion_dlq_messages.alarm_name
}

output "conversion_queue_age_alarm_name" {
  value = aws_cloudwatch_metric_alarm.conversion_queue_age.alarm_name
}
