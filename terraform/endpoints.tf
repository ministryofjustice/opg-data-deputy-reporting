module "endpoints_healthcheck" {
  source = "./modules/endpoints"
  lambda = module.lamdba_healthcheck.lambda
  //lambda_name                                = module.lamdba_healthcheck.lambda.function_name
  //lambda_arn                                 = module.lamdba_healthcheck.lambda.arn
  region                                     = data.aws_region.region.name
  deputy_reporting_api_gateway_allowed_roles = local.deputy_reporting_api_gateway_allowed_roles
  //lambda_invoke_arn                          = module.lamdba_healthcheck.lambda.invoke_arn
  deputy_reporting_api_gateway = aws_api_gateway_rest_api.deputy_reporting_api_gateway
  resource_part_1              = "digital-deputy"
  resource_part_2              = "healthcheck"
  method                       = "GET"
}

resource "aws_iam_role_policy_attachment" "deputy_reporting_access_policy_attachment" {
  role       = module.endpoints_healthcheck.data_deputy_reporting.name
  policy_arn = module.endpoints_healthcheck.deputy_reporting_access_policy.arn //api collections gateway
}
