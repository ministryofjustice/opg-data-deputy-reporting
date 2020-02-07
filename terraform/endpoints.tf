module "endpoints_healthcheck" {
  source                                     = "./modules/endpoints"
  lambda                                     = module.lamdba_healthcheck.lambda
  environment                                = local.environment
  region                                     = data.aws_region.region.name
  deputy_reporting_api_gateway_allowed_roles = local.account["allowed_roles"]
  deputy_reporting_api_gateway               = aws_api_gateway_rest_api.deputy_reporting_api_gateway
  resource_part_1                            = "healthcheck"
  method                                     = "GET"
}

resource "aws_iam_role_policy_attachment" "access_policy_attachment" {
  role       = module.endpoints_healthcheck.data_deputy_reporting.name
  policy_arn = module.endpoints_healthcheck.access_policy.arn
}
