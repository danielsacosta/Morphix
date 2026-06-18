locals {
  name          = "${var.project_name}-${var.environment}"
  input_bucket  = var.input_bucket_name != "" ? var.input_bucket_name : "${local.name}-input"
  output_bucket = var.output_bucket_name != "" ? var.output_bucket_name : "${local.name}-output"
}

resource "aws_s3_bucket" "input" {
  bucket        = local.input_bucket
  force_destroy = var.force_destroy
  tags          = merge(var.tags, { Name = local.input_bucket })
}

resource "aws_s3_bucket" "output" {
  bucket        = local.output_bucket
  force_destroy = var.force_destroy
  tags          = merge(var.tags, { Name = local.output_bucket })
}

resource "aws_s3_bucket_public_access_block" "input" {
  bucket                  = aws_s3_bucket.input.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "output" {
  bucket                  = aws_s3_bucket.output.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "input" {
  bucket = aws_s3_bucket.input.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "output" {
  bucket = aws_s3_bucket.output.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "input" {
  bucket = aws_s3_bucket.input.id

  rule {
    id     = "expire-input-files"
    status = "Enabled"

    expiration {
      days = var.input_retention_days
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "output" {
  bucket = aws_s3_bucket.output.id

  rule {
    id     = "expire-output-files"
    status = "Enabled"

    expiration {
      days = var.output_retention_days
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "input" {
  bucket = aws_s3_bucket.input.id

  cors_rule {
    allowed_headers = ["Content-Type", "x-amz-*"]
    allowed_methods = ["PUT"]
    allowed_origins = var.allowed_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 900
  }
}

