include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../blueprints/modules/frontend"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

inputs = {
  project_name           = local.root.locals.project_name
  environment            = local.root.locals.environment
  frontend_bucket_name   = get_env("FRONTEND_BUCKET_NAME", "")
  frontend_force_destroy = false
  frontend_price_class   = "PriceClass_100"
  tags                   = local.root.locals.tags
}

