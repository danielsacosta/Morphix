output "worker_repository_url" {
  value = aws_ecr_repository.worker.repository_url
}

output "worker_log_group_name" {
  value = aws_cloudwatch_log_group.worker.name
}

output "worker_task_definition_arn" {
  value = aws_ecs_task_definition.worker.arn
}

output "worker_task_execution_role_arn" {
  value = aws_iam_role.execution.arn
}

output "worker_task_role_arn" {
  value = aws_iam_role.task.arn
}

output "worker_security_group_id" {
  value = aws_security_group.worker.id
}

output "worker_service_name" {
  value = aws_ecs_service.worker.name
}

output "worker_private_subnet_ids" {
  value = var.private_subnet_ids
}
