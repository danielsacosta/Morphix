include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/api"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
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
    jobs_table_name = "morphix-dev-jobs"
    jobs_table_arn  = "arn:aws:dynamodb:us-east-1:000000000000:table/morphix-dev-jobs"
  }
}

dependency "step_functions" {
  config_path = "../../shared/step-functions"
  mock_outputs = {
    state_machine_arn = "arn:aws:states:us-east-1:000000000000:stateMachine:morphix-dev-conversion"
  }
}

inputs = {
  project_name       = local.root.locals.project_name
  environment        = local.root.locals.environment
  aws_region         = local.root.locals.aws_region
  api_image_uri      = get_env("API_IMAGE_URI", "")
  jobs_table_name    = dependency.jobs_db.outputs.jobs_table_name
  jobs_table_arn     = dependency.jobs_db.outputs.jobs_table_arn
  input_bucket_name  = dependency.storage.outputs.input_bucket_name
  input_bucket_arn   = dependency.storage.outputs.input_bucket_arn
  output_bucket_name = dependency.storage.outputs.output_bucket_name
  output_bucket_arn  = dependency.storage.outputs.output_bucket_arn
  state_machine_arn  = dependency.step_functions.outputs.state_machine_arn
  max_file_size_mb   = 100
  allowed_origins    = split(",", get_env("ALLOWED_ORIGINS", "http://localhost:5173"))
  tags               = local.root.locals.tags
}
