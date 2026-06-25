include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/conversion-queue"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

inputs = {
  project_name               = local.root.locals.project_name
  environment                = local.root.locals.environment
  visibility_timeout_seconds = 1200
  receive_wait_time_seconds  = 20
  max_receive_count          = 3
  tags                       = local.root.locals.tags
}
