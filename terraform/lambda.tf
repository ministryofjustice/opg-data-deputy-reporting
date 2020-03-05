module "lamdba_healthcheck" {
  source                 = "./modules/lambda"
  environment            = local.environment
  aws_subnet_ids         = data.aws_subnet_ids.private.ids
  target_environment     = local.account.target_environment
  vpc_id                 = local.account.vpc_id
  lambda_prefix          = "sirius-healthcheck"
  handler                = "healthcheck.lambda_handler"
  lambda_function_subdir = "healthcheck"
  logger_level           = "INFO"
}

module "lambda_reports" {
  source                 = "./modules/lambda"
  environment            = local.environment
  aws_subnet_ids         = data.aws_subnet_ids.private.ids
  target_environment     = local.account.target_environment
  vpc_id                 = local.account.vpc_id
  lambda_prefix          = "sirius-reports"
  handler                = "reports.app"
  lambda_function_subdir = "reports"
  logger_level           = "INFO"
}

