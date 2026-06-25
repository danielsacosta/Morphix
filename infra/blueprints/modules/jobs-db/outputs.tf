output "jobs_table_name" {
  value = aws_dynamodb_table.jobs.name
}

output "jobs_table_arn" {
  value = aws_dynamodb_table.jobs.arn
}

output "jobs_table_stream_arn" {
  value = aws_dynamodb_table.jobs.stream_arn
}
