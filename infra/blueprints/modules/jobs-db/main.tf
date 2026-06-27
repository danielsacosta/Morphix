locals {
  name = "${var.project_name}-${var.environment}-jobs"
}

resource "aws_dynamodb_table" "jobs" {
  name         = local.name
  billing_mode = var.billing_mode
  hash_key     = "job_id"

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "job_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "updated_at"
    type = "S"
  }

  global_secondary_index {
    name            = "GSI1"
    projection_type = "ALL"

    key_schema {
      attribute_name = "user_id"
      key_type       = "HASH"
    }

    key_schema {
      attribute_name = "created_at"
      key_type       = "RANGE"
    }
  }

  global_secondary_index {
    name            = "GSI2"
    projection_type = "ALL"

    key_schema {
      attribute_name = "status"
      key_type       = "HASH"
    }

    key_schema {
      attribute_name = "updated_at"
      key_type       = "RANGE"
    }
  }

  ttl {
    attribute_name = var.ttl_attribute
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = merge(var.tags, {
    Name = local.name
  })
}
