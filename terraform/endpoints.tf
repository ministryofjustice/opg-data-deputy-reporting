module "endpoints_healthcheck" {
  source                                     = "./modules/endpoints"
  lambda                                     = module.lamdba_healthcheck.lambda
  region                                     = data.aws_region.region.name
  deputy_reporting_api_gateway_allowed_roles = local.deputy_reporting_api_gateway_allowed_roles
  deputy_reporting_api_gateway               = aws_api_gateway_rest_api.deputy_reporting_api_gateway
  resource_part_1                            = "digital-deputy"
  resource_part_2                            = "healthcheck"
  method                                     = "GET"
}

resource "aws_iam_role_policy_attachment" "access_policy_attachment" {
  role       = module.endpoints_healthcheck.data_deputy_reporting.name
  policy_arn = module.endpoints_healthcheck.access_policy.arn //api collections gateway
}
