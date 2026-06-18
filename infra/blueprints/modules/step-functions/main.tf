locals {
  name      = "${var.project_name}-${var.environment}"
  log_group = "/aws/stepfunctions/${local.name}-conversion"
}

resource "aws_cloudwatch_log_group" "conversion" {
  name              = local.log_group
  retention_in_days = 14
  tags              = var.tags
}

data "aws_iam_policy_document" "assume" {
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
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

data "aws_iam_policy_document" "state_machine" {
  statement {
    sid       = "RunWorkerTask"
    actions   = ["ecs:RunTask", "ecs:StopTask", "ecs:DescribeTasks"]
    resources = ["*"]
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

locals {
  definition = jsonencode({
    Comment = "Morphix asynchronous conversion workflow"
    StartAt = "MarkProcessing"
    States = {
      MarkProcessing = {
        Type     = "Task"
        Resource = "arn:aws:states:::dynamodb:updateItem"
        Parameters = {
          TableName = var.jobs_table_name
          Key = {
            job_id = {
              "S.$" = "$.job_id"
            }
          }
          UpdateExpression = "SET #status = :status, #updated_at = :updated_at"
          ExpressionAttributeNames = {
            "#status"     = "status"
            "#updated_at" = "updated_at"
          }
          ExpressionAttributeValues = {
            ":status" = {
              S = "PROCESSING"
            }
            ":updated_at" = {
              "S.$" = "$$.State.EnteredTime"
            }
          }
        }
        ResultPath = null
        Next       = "RunWorker"
      }
      RunWorker = {
        Type     = "Task"
        Resource = "arn:aws:states:::ecs:runTask.sync"
        Parameters = {
          LaunchType      = "FARGATE"
          Cluster         = var.cluster_arn
          TaskDefinition  = var.task_definition_arn
          PlatformVersion = "LATEST"
          NetworkConfiguration = {
            AwsvpcConfiguration = {
              AssignPublicIp = "DISABLED"
              SecurityGroups = [var.worker_security_group_id]
              Subnets        = var.private_subnet_ids
            }
          }
          Overrides = {
            ContainerOverrides = [
              {
                Name = "worker"
                Environment = [
                  {
                    Name      = "JOB_PAYLOAD"
                    "Value.$" = "States.JsonToString($)"
                  }
                ]
              }
            ]
          }
        }
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "ECS.AmazonECSException"]
            IntervalSeconds = 10
            MaxAttempts     = 2
            BackoffRate     = 2
          }
        ]
        ResultPath = "$.worker_result"
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "MarkFailed"
          }
        ]
        Next = "MarkCompleted"
      }
      MarkCompleted = {
        Type     = "Task"
        Resource = "arn:aws:states:::dynamodb:updateItem"
        Parameters = {
          TableName = var.jobs_table_name
          Key = {
            job_id = {
              "S.$" = "$.job_id"
            }
          }
          UpdateExpression = "SET #status = :status, #updated_at = :updated_at"
          ExpressionAttributeNames = {
            "#status"     = "status"
            "#updated_at" = "updated_at"
          }
          ExpressionAttributeValues = {
            ":status" = {
              S = "COMPLETED"
            }
            ":updated_at" = {
              "S.$" = "$$.State.EnteredTime"
            }
          }
        }
        End = true
      }
      MarkFailed = {
        Type     = "Task"
        Resource = "arn:aws:states:::dynamodb:updateItem"
        Parameters = {
          TableName = var.jobs_table_name
          Key = {
            job_id = {
              "S.$" = "$.job_id"
            }
          }
          UpdateExpression = "SET #status = :status, #updated_at = :updated_at, #error_message = :error_message"
          ExpressionAttributeNames = {
            "#status"        = "status"
            "#updated_at"    = "updated_at"
            "#error_message" = "error_message"
          }
          ExpressionAttributeValues = {
            ":status" = {
              S = "FAILED"
            }
            ":updated_at" = {
              "S.$" = "$$.State.EnteredTime"
            }
            ":error_message" = {
              S = "No fue posible convertir el archivo. Verifica que el archivo no este corrupto."
            }
          }
        }
        End = true
      }
    }
  })
}

resource "aws_sfn_state_machine" "conversion" {
  name     = "${local.name}-conversion"
  role_arn = aws_iam_role.state_machine.arn
  type     = "STANDARD"

  logging_configuration {
    include_execution_data = false
    level                  = "ERROR"
    log_destination        = "${aws_cloudwatch_log_group.conversion.arn}:*"
  }

  definition = local.definition
  tags       = var.tags
}
