include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../blueprints/modules/frontend"
}

locals {
  root = read_terragrunt_config(find_in_parent_folders("root.hcl"))
}

dependency "api" {
  config_path = "../../live/services/api"
  mock_outputs = {
    api_endpoint       = "http://localhost:8000"
    websocket_endpoint = "ws://localhost:8001/dev"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan", "destroy"]
}

inputs = {
  project_name           = local.root.locals.project_name
  environment            = local.root.locals.environment
  frontend_bucket_name   = get_env("FRONTEND_BUCKET_NAME", "")
  frontend_force_destroy = get_env("FRONTEND_FORCE_DESTROY", "false") == "true"
  frontend_price_class   = "PriceClass_100"
  api_base_url           = dependency.api.outputs.api_endpoint
  websocket_api_url      = dependency.api.outputs.websocket_endpoint
  max_file_size_mb       = 100
  tags                   = local.root.locals.tags
}
