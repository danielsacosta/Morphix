include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/api"
}

locals {
  root                    = read_terragrunt_config(find_in_parent_folders("root.hcl"))
  frontend_origin         = get_env("FRONTEND_ORIGIN", "")
  default_allowed_origins = local.frontend_origin != "" ? "http://localhost:5173,${local.frontend_origin}" : "http://localhost:5173"
  browser_allowed_origins = get_env("ALLOWED_ORIGINS", local.default_allowed_origins)
}

dependency "storage" {
  config_path = "../../shared/storage"
  mock_outputs = {
    input_bucket_name  = "morphix-dev-input"
    input_bucket_arn   = "arn:aws:s3:::morphix-dev-input"
    output_bucket_name = "morphix-dev-output"
    output_bucket_arn  = "arn:aws:s3:::morphix-dev-output"
  }
}

dependency "jobs_db" {
  config_path = "../../shared/jobs-db"
  mock_outputs = {
    jobs_table_name       = "morphix-dev-jobs"
    jobs_table_arn        = "arn:aws:dynamodb:us-east-1:000000000000:table/morphix-dev-jobs"
    jobs_table_stream_arn = "arn:aws:dynamodb:us-east-1:000000000000:table/morphix-dev-jobs/stream/2026-06-24T00:00:00.000"
  }
}

dependency "conversion_queue" {
  config_path = "../../shared/conversion-queue"
  mock_outputs = {
    queue_url = "https://sqs.us-east-1.amazonaws.com/000000000000/morphix-dev-conversions"
    queue_arn = "arn:aws:sqs:us-east-1:000000000000:morphix-dev-conversions"
  }
}

inputs = {
  project_name                    = local.root.locals.project_name
  environment                     = local.root.locals.environment
  aws_region                      = local.root.locals.aws_region
  api_package_path                = get_env("API_LAMBDA_PACKAGE", "")
  state_machine_definition_path   = "${get_terragrunt_dir()}/../../../../../apps/api/state_machine_definition.json"
  jobs_table_name                 = dependency.jobs_db.outputs.jobs_table_name
  jobs_table_arn                  = dependency.jobs_db.outputs.jobs_table_arn
  jobs_table_stream_arn           = dependency.jobs_db.outputs.jobs_table_stream_arn
  input_bucket_name               = dependency.storage.outputs.input_bucket_name
  input_bucket_arn                = dependency.storage.outputs.input_bucket_arn
  output_bucket_name              = dependency.storage.outputs.output_bucket_name
  output_bucket_arn               = dependency.storage.outputs.output_bucket_arn
  conversion_queue_url            = dependency.conversion_queue.outputs.queue_url
  conversion_queue_arn            = dependency.conversion_queue.outputs.queue_arn
  worker_callback_timeout_seconds = 1200
  max_file_size_mb                = 100
  allowed_origins                 = [for origin in split(",", local.browser_allowed_origins) : trimspace(origin) if trimspace(origin) != ""]
  tags                            = local.root.locals.tags
}
