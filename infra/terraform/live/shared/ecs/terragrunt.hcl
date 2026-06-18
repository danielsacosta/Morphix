include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/ecs-cluster"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

inputs = {
  project_name              = local.root.locals.project_name
  environment               = local.root.locals.environment
  enable_container_insights = true
  tags                      = local.root.locals.tags
}

