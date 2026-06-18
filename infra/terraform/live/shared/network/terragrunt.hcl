include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/network"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

inputs = {
  project_name                    = local.root.locals.project_name
  environment                     = local.root.locals.environment
  aws_region                      = local.root.locals.aws_region
  vpc_cidr                        = "10.30.0.0/16"
  public_subnet_cidrs             = ["10.30.0.0/24", "10.30.1.0/24"]
  private_subnet_cidrs            = ["10.30.10.0/24", "10.30.11.0/24"]
  enable_nat_gateway              = true
  enable_s3_endpoint              = true
  enable_dynamodb_endpoint        = true
  enable_ecr_endpoints            = false
  enable_cloudwatch_logs_endpoint = false
  tags                            = local.root.locals.tags
}
