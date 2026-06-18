include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/fargate-worker"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

dependency "network" {
  config_path = "../../shared/network"
  mock_outputs = {
    vpc_id             = "vpc-00000000000000000"
    private_subnet_ids = ["subnet-00000000000000000", "subnet-11111111111111111"]
  }
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

dependency "ecs" {
  config_path = "../../shared/ecs"
  mock_outputs = {
    cluster_arn = "arn:aws:ecs:us-east-1:000000000000:cluster/morphix-dev-cluster"
  }
}

inputs = {
  project_name                 = local.root.locals.project_name
  environment                  = local.root.locals.environment
  aws_region                   = local.root.locals.aws_region
  cluster_arn                  = dependency.ecs.outputs.cluster_arn
  vpc_id                       = dependency.network.outputs.vpc_id
  private_subnet_ids           = dependency.network.outputs.private_subnet_ids
  worker_image_uri             = get_env("WORKER_IMAGE_URI", "")
  worker_cpu                   = 1024
  worker_memory                = 2048
  worker_ephemeral_storage_gib = 30
  input_bucket_arn             = dependency.storage.outputs.input_bucket_arn
  output_bucket_arn            = dependency.storage.outputs.output_bucket_arn
  input_bucket_name            = dependency.storage.outputs.input_bucket_name
  output_bucket_name           = dependency.storage.outputs.output_bucket_name
  jobs_table_arn               = dependency.jobs_db.outputs.jobs_table_arn
  jobs_table_name              = dependency.jobs_db.outputs.jobs_table_name
  conversion_timeout_seconds   = 900
  tags                         = local.root.locals.tags
}
