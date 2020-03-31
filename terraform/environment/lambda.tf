module "lamdba_healthcheck_1" {
  source                 = "./modules/lambda"
  environment            = local.environment
  aws_subnet_ids         = data.aws_subnet_ids.private.ids
  target_environment     = local.account.target_environment
  vpc_id                 = local.account.vpc_id
  lambda_prefix          = "sirius-healthcheck"
  handler                = "healthcheck.lambda_handler"
  lambda_function_subdir = "healthcheck"
  logger_level           = "INFO"
  tags                   = local.default_tags
  openapi_version        = "1_0_0"
  rest_api               = aws_api_gateway_rest_api.deputy_reporting
}

module "lambda_reports_1" {
  source                 = "./modules/lambda"
  environment            = local.environment
  aws_subnet_ids         = data.aws_subnet_ids.private.ids
  target_environment     = local.account.target_environment
  vpc_id                 = local.account.vpc_id
  lambda_prefix          = "sirius-reports"
  handler                = "reports.lambda_handler"
  lambda_function_subdir = "reports"
  logger_level           = "INFO"
  tags                   = local.default_tags
  openapi_version        = "1_0_0"
  rest_api               = aws_api_gateway_rest_api.deputy_reporting
}

//To Add New Version Copy and Paste Above and Modify Accordingly
