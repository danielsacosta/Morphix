include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../blueprints/modules/storage"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

inputs = {
  project_name          = local.root.locals.project_name
  environment           = local.root.locals.environment
  input_retention_days  = 1
  output_retention_days = 7
  max_upload_size_mb    = 100
  allowed_origins       = split(",", get_env("ALLOWED_ORIGINS", "http://localhost:5173"))
  tags                  = local.root.locals.tags
}

