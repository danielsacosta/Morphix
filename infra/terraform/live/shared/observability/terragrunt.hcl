include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/observability"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

dependency "jobs_db" {
  config_path = "../jobs-db"
  mock_outputs = {
    jobs_table_name = "morphix-dev-jobs"
  }
}

dependency "worker" {
  config_path = "../../services/worker"
  mock_outputs = {
    worker_log_group_name = "/aws/ecs/morphix-dev-worker"
  }
}

dependency "step_functions" {
  config_path = "../step-functions"
  mock_outputs = {
    state_machine_arn  = "arn:aws:states:us-east-1:000000000000:stateMachine:morphix-dev-conversion"
    state_machine_name = "morphix-dev-conversion"
  }
}

dependency "api" {
  config_path = "../../services/api"
  mock_outputs = {
    api_log_group_name = "/aws/lambda/morphix-dev-api"
  }
}

inputs = {
  project_name                = local.root.locals.project_name
  environment                 = local.root.locals.environment
  aws_region                  = local.root.locals.aws_region
  api_log_group_name          = dependency.api.outputs.api_log_group_name
  worker_log_group_name       = dependency.worker.outputs.worker_log_group_name
  state_machine_arn           = dependency.step_functions.outputs.state_machine_arn
  state_machine_name          = dependency.step_functions.outputs.state_machine_name
  jobs_table_name             = dependency.jobs_db.outputs.jobs_table_name
  failed_jobs_alarm_threshold = 5
  tags                        = local.root.locals.tags
}
