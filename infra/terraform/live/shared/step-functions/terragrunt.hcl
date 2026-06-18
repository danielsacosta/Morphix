include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/step-functions"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

dependency "network" {
  config_path = "../network"
  mock_outputs = {
    private_subnet_ids = ["subnet-00000000000000000", "subnet-11111111111111111"]
  }
}

dependency "ecs" {
  config_path = "../ecs"
  mock_outputs = {
    cluster_arn = "arn:aws:ecs:us-east-1:000000000000:cluster/morphix-dev-cluster"
  }
}

dependency "jobs_db" {
  config_path = "../jobs-db"
  mock_outputs = {
    jobs_table_name = "morphix-dev-jobs"
    jobs_table_arn  = "arn:aws:dynamodb:us-east-1:000000000000:table/morphix-dev-jobs"
  }
}

dependency "worker" {
  config_path = "../../services/worker"
  mock_outputs = {
    worker_task_definition_arn     = "arn:aws:ecs:us-east-1:000000000000:task-definition/morphix-dev-worker:1"
    worker_task_execution_role_arn = "arn:aws:iam::000000000000:role/morphix-dev-worker-execution"
    worker_task_role_arn           = "arn:aws:iam::000000000000:role/morphix-dev-worker-task"
    worker_security_group_id       = "sg-00000000000000000"
  }
}

inputs = {
  project_name             = local.root.locals.project_name
  environment              = local.root.locals.environment
  cluster_arn              = dependency.ecs.outputs.cluster_arn
  task_definition_arn      = dependency.worker.outputs.worker_task_definition_arn
  task_execution_role_arn  = dependency.worker.outputs.worker_task_execution_role_arn
  task_role_arn            = dependency.worker.outputs.worker_task_role_arn
  worker_security_group_id = dependency.worker.outputs.worker_security_group_id
  private_subnet_ids       = dependency.network.outputs.private_subnet_ids
  jobs_table_name          = dependency.jobs_db.outputs.jobs_table_name
  jobs_table_arn           = dependency.jobs_db.outputs.jobs_table_arn
  tags                     = local.root.locals.tags
}

