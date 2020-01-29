module "endpoints_healthcheck" {
  source                                     = "./modules/endpoints"
  gateway_path_product                       = "healthcheck"
  gateway_path_collection                    = "deputy-reporting"
  lambda_name                                = module.lamdba_healthcheck.lambda_name
  lambda_arn                                 = module.lamdba_healthcheck.lambda_arn
  region                                     = data.aws_region.region.name
  deputy_reporting_api_gateway_allowed_roles = local.deputy_reporting_api_gateway_allowed_roles
}

