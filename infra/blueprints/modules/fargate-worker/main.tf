locals {
  name      = "${var.project_name}-${var.environment}"
  image_uri = var.worker_image_uri != "" ? var.worker_image_uri : "${aws_ecr_repository.worker.repository_url}:latest"
  log_group = "/aws/ecs/${local.name}-worker"
}

resource "aws_ecr_repository" "worker" {
  name                 = "${local.name}-worker"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.repository_force_delete

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = var.tags
}

resource "aws_ecr_lifecycle_policy" "worker" {
  repository = aws_ecr_repository.worker.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 20 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 20
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = local.log_group
  retention_in_days = 14
  tags              = var.tags
}

data "aws_iam_policy_document" "ecs_tasks_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "${local.name}-worker-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "task" {
  name               = "${local.name}-worker-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json
  tags               = var.tags
}

data "aws_iam_policy_document" "task" {
  statement {
    sid     = "ReadInputWriteOutput"
    actions = ["s3:GetObject", "s3:PutObject", "s3:AbortMultipartUpload"]
    resources = [
      "${var.input_bucket_arn}/*",
      "${var.output_bucket_arn}/*",
    ]
  }

  statement {
    sid       = "ListBuckets"
    actions   = ["s3:ListBucket"]
    resources = [var.input_bucket_arn, var.output_bucket_arn]
  }

  statement {
    sid       = "UpdateJobs"
    actions   = ["dynamodb:GetItem", "dynamodb:UpdateItem"]
    resources = [var.jobs_table_arn]
  }

  statement {
    sid = "ConsumeConversionQueue"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:ChangeMessageVisibility",
      "sqs:GetQueueAttributes"
    ]
    resources = [var.conversion_queue_arn]
  }

  statement {
    sid = "ReportStepFunctionsTaskResult"
    actions = [
      "states:SendTaskFailure",
      "states:SendTaskSuccess"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "task" {
  name   = "${local.name}-worker-policy"
  role   = aws_iam_role.task.id
  policy = data.aws_iam_policy_document.task.json
}

resource "aws_security_group" "worker" {
  name        = "${local.name}-worker"
  description = "Morphix conversion worker egress"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${local.name}-worker-sg"
  })
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${local.name}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = tostring(var.worker_cpu)
  memory                   = tostring(var.worker_memory)
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  ephemeral_storage {
    size_in_gib = var.worker_ephemeral_storage_gib
  }

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = local.image_uri
      essential = true
      environment = [
        { name = "PROJECT_NAME", value = var.project_name },
        { name = "ENVIRONMENT", value = var.environment },
        { name = "AWS_REGION", value = var.aws_region },
        { name = "JOBS_TABLE_NAME", value = var.jobs_table_name },
        { name = "INPUT_BUCKET", value = var.input_bucket_name },
        { name = "OUTPUT_BUCKET", value = var.output_bucket_name },
        { name = "CONVERSION_QUEUE_URL", value = var.conversion_queue_url },
        { name = "QUEUE_WAIT_TIME_SECONDS", value = "20" },
        { name = "WORKDIR", value = "/tmp/morphix" },
        { name = "CONVERSION_TIMEOUT_SECONDS", value = tostring(var.conversion_timeout_seconds) }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.worker.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "worker"
        }
      }
    }
  ])

  tags = var.tags
}

resource "aws_ecs_service" "worker" {
  name            = "${local.name}-worker"
  cluster         = var.cluster_arn
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    assign_public_ip = false
    security_groups  = [aws_security_group.worker.id]
    subnets          = var.private_subnet_ids
  }

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  tags = var.tags
}
