module "lamdba_healthcheck_v1" {
  source                 = "./modules/lambda"
  environment            = local.environment
  aws_subnet_ids         = data.aws_subnet_ids.private.ids
  lambda_prefix          = "sirius-healthcheck"
  handler                = "healthcheck.lambda_handler"
  lambda_function_subdir = "healthcheck"
  tags                   = local.default_tags
  openapi_version        = "v1"
  rest_api               = aws_api_gateway_rest_api.deputy_reporting
  account                = local.account
  target_environment     = local.target_environment
}

module "lambda_reports_v1" {
  source                 = "./modules/lambda"
  environment            = local.environment
  aws_subnet_ids         = data.aws_subnet_ids.private.ids
  lambda_prefix          = "sirius-reports"
  handler                = "app.reports.lambda_handler"
  lambda_function_subdir = "reports"
  tags                   = local.default_tags
  openapi_version        = "v1"
  rest_api               = aws_api_gateway_rest_api.deputy_reporting
  account                = local.account
  target_environment     = local.target_environment
}

module "lambda_supporting_docs_v1" {
  source                 = "./modules/lambda"
  environment            = local.environment
  aws_subnet_ids         = data.aws_subnet_ids.private.ids
  lambda_prefix          = "sirius-supporting_docs"
  handler                = "app.supporting_docs.lambda_handler"
  lambda_function_subdir = "supporting_docs"
  tags                   = local.default_tags
  openapi_version        = "v1"
  rest_api               = aws_api_gateway_rest_api.deputy_reporting
  account                = local.account
  target_environment     = local.target_environment
}

module "lambda_checklists_v1" {
  source                 = "./modules/lambda"
  environment            = local.environment
  aws_subnet_ids         = data.aws_subnet_ids.private.ids
  lambda_prefix          = "sirius-checklists"
  handler                = "app.checklists.lambda_handler"
  lambda_function_subdir = "checklists"
  tags                   = local.default_tags
  openapi_version        = "v1"
  rest_api               = aws_api_gateway_rest_api.deputy_reporting
  account                = local.account
  target_environment     = local.target_environment
}

//Modify here for new version
module "lamdba_flask_v2" {
  source                 = "./modules/lambda"
  environment            = local.environment
  aws_subnet_ids         = data.aws_subnet_ids.private.ids
  lambda_prefix          = "deputy-reporting"
  handler                = "app.docs.lambda_handler"
  lambda_function_subdir = "documents"
  tags                   = local.default_tags
  openapi_version        = "v2"
  rest_api               = aws_api_gateway_rest_api.deputy_reporting
  account                = local.account
  target_environment     = local.target_environment
}
