include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/jobs-db"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

inputs = {
  project_name  = local.root.locals.project_name
  environment   = local.root.locals.environment
  billing_mode  = "PAY_PER_REQUEST"
  ttl_attribute = "expires_at"
  tags          = local.root.locals.tags
}

