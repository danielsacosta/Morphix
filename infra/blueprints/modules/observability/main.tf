locals {
  name = "${var.project_name}-${var.environment}"
}

resource "aws_cloudwatch_log_metric_filter" "worker_failures" {
  name           = "${local.name}-worker-failures"
  log_group_name = var.worker_log_group_name
  pattern        = "\"FAILED\""

  metric_transformation {
    name      = "WorkerFailedJobs"
    namespace = "Morphix/${var.environment}"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "worker_failures" {
  alarm_name          = "${local.name}-worker-failures"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.worker_failures.metric_transformation[0].name
  namespace           = "Morphix/${var.environment}"
  period              = 300
  statistic           = "Sum"
  threshold           = var.failed_jobs_alarm_threshold
  treat_missing_data  = "notBreaching"
  tags                = var.tags
}

resource "aws_cloudwatch_metric_alarm" "step_functions_failed" {
  alarm_name          = "${local.name}-step-functions-failed"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ExecutionsFailed"
  namespace           = "AWS/States"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    StateMachineArn = var.state_machine_arn
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "conversion_dlq_messages" {
  alarm_name          = "${local.name}-conversion-dlq-messages"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = var.conversion_dlq_name
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "conversion_queue_age" {
  alarm_name          = "${local.name}-conversion-queue-age"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "ApproximateAgeOfOldestMessage"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = var.oldest_message_age_alarm_seconds
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = var.conversion_queue_name
  }

  tags = var.tags
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name}-operations"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "Step Functions executions"
          region  = var.aws_region
          metrics = [["AWS/States", "ExecutionsStarted", "StateMachineArn", var.state_machine_arn], [".", "ExecutionsFailed", ".", "."]]
          stat    = "Sum"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Conversion queue"
          region = var.aws_region
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", var.conversion_queue_name],
            [".", "ApproximateNumberOfMessagesNotVisible", ".", "."],
            [".", "ApproximateAgeOfOldestMessage", ".", ".", { stat = "Maximum", yAxis = "right" }],
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", var.conversion_dlq_name]
          ]
          stat   = "Sum"
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "DynamoDB jobs table"
          region  = var.aws_region
          metrics = [["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", var.jobs_table_name], [".", "ConsumedWriteCapacityUnits", ".", "."]]
          stat    = "Sum"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        properties = {
          title  = "Recent worker errors"
          region = var.aws_region
          query  = "SOURCE '${var.worker_log_group_name}' | fields @timestamp, @message | filter @message like /FAILED|ERROR|Exception/ | sort @timestamp desc | limit 50"
        }
      }
    ]
  })
}
