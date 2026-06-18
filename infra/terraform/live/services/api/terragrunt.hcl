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

dependency "network" {
  config_path = "../../shared/network"
  mock_outputs = {
    private_subnet_ids = ["subnet-00000000000000000", "subnet-11111111111111111"]
  }
}

dependency "ecs" {
  config_path = "../../shared/ecs"
  mock_outputs = {
    cluster_arn = "arn:aws:ecs:us-east-1:000000000000:cluster/morphix-dev-cluster"
  }
}

dependency "worker" {
  config_path = "../worker"
  mock_outputs = {
    worker_task_definition_arn     = "arn:aws:ecs:us-east-1:000000000000:task-definition/morphix-dev-worker:1"
    worker_task_execution_role_arn = "arn:aws:iam::000000000000:role/morphix-dev-worker-execution"
    worker_task_role_arn           = "arn:aws:iam::000000000000:role/morphix-dev-worker-task"
    worker_security_group_id       = "sg-00000000000000000"
  }
}

inputs = {
  project_name                  = local.root.locals.project_name
  environment                   = local.root.locals.environment
  aws_region                    = local.root.locals.aws_region
  api_package_path              = get_env("API_LAMBDA_PACKAGE", "")
  state_machine_definition_path = "${get_terragrunt_dir()}/../../../../../apps/api/state_machine_definition.json"
  jobs_table_name               = dependency.jobs_db.outputs.jobs_table_name
  jobs_table_arn                = dependency.jobs_db.outputs.jobs_table_arn
  input_bucket_name             = dependency.storage.outputs.input_bucket_name
  input_bucket_arn              = dependency.storage.outputs.input_bucket_arn
  output_bucket_name            = dependency.storage.outputs.output_bucket_name
  output_bucket_arn             = dependency.storage.outputs.output_bucket_arn
  cluster_arn                   = dependency.ecs.outputs.cluster_arn
  task_definition_arn           = dependency.worker.outputs.worker_task_definition_arn
  task_execution_role_arn       = dependency.worker.outputs.worker_task_execution_role_arn
  task_role_arn                 = dependency.worker.outputs.worker_task_role_arn
  worker_security_group_id      = dependency.worker.outputs.worker_security_group_id
  private_subnet_ids            = dependency.network.outputs.private_subnet_ids
  max_file_size_mb              = 100
  allowed_origins               = split(",", get_env("ALLOWED_ORIGINS", "http://localhost:5173"))
  tags                          = local.root.locals.tags
}
