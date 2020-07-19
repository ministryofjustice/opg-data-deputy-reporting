locals {
  certificate_arn = local.branch_build_flag ? data.aws_acm_certificate.environment_cert[0].arn : aws_acm_certificate.environment_cert[0].arn
  certificate     = local.branch_build_flag ? data.aws_acm_certificate.environment_cert[0] : aws_acm_certificate.environment_cert[0]
}

resource "aws_api_gateway_method_settings" "global_gateway_settings" {
  rest_api_id = aws_api_gateway_rest_api.deputy_reporting.id
  //Modify here for new version
  //stage_name = module.deploy_v2.stage.stage_name
  stage_name  = module.deploy_v1.stage.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }

}

resource "aws_api_gateway_domain_name" "sirius_deputy_reporting" {
  domain_name              = trimsuffix(local.a_record, ".")
  regional_certificate_arn = local.certificate_arn

  depends_on = [local.certificate]
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = local.default_tags
}

module "deploy_v1" {
  source                = "./modules/stage"
  environment           = local.environment
  aws_subnet_ids        = data.aws_subnet_ids.private.ids
  target_environment    = local.account.target_environment
  vpc_id                = local.account.vpc_id
  tags                  = local.default_tags
  api_name              = local.api_name
  openapi_version       = "v1"
  reports_lambda        = module.lambda_reports_v1.lambda
  healthcheck_lambda    = module.lamdba_healthcheck_v1.lambda
  supportingdocs_lambda = module.lambda_supporting_docs_v1.lambda
  checklists_lambda     = module.lambda_checklists_v1.lambda
  //Modify here for new version
  flaskapp_lambda = "non existant"
  //flaskapp_lambda       = module.lamdba_flask_v2.lambda
  rest_api    = aws_api_gateway_rest_api.deputy_reporting
  domain_name = aws_api_gateway_domain_name.sirius_deputy_reporting
}

//Modify here for new version
//module "deploy_v2" {
//  source                = "./modules/stage"
//  environment           = local.environment
//  aws_subnet_ids        = data.aws_subnet_ids.private.ids
//  target_environment    = local.account.target_environment
//  vpc_id                = local.account.vpc_id
//  tags                  = local.default_tags
//  api_name              = local.api_name
//  openapi_version       = "v2"
//  reports_lambda        = module.lambda_reports_v1.lambda
//  healthcheck_lambda    = module.lamdba_healthcheck_v1.lambda
//  supportingdocs_lambda = module.lambda_supporting_docs_v1.lambda
//  checklists_lambda     = module.lambda_checklists_v1.lambda
//  flaskapp_lambda       = module.lamdba_flask_v2.lambda
//  rest_api              = aws_api_gateway_rest_api.deputy_reporting
//  domain_name           = aws_api_gateway_domain_name.sirius_deputy_reporting
//}

//To Add New Version Copy and Paste Above and Modify Accordingly
//Below takes the latest stage/deployment. Modify for new version.

//Modify here for new version
resource "aws_api_gateway_base_path_mapping" "mapping" {
  api_id      = aws_api_gateway_rest_api.deputy_reporting.id
  stage_name  = module.deploy_v1.deployment.stage_name
  domain_name = aws_api_gateway_domain_name.sirius_deputy_reporting.domain_name
  base_path   = module.deploy_v1.deployment.stage_name
}

//resource "aws_api_gateway_base_path_mapping" "mapping_v2" {
//  api_id      = aws_api_gateway_rest_api.deputy_reporting.id
//  stage_name  = module.deploy_v2.deployment.stage_name
//  domain_name = aws_api_gateway_domain_name.sirius_deputy_reporting.domain_name
//  base_path   = module.deploy_v2.deployment.stage_name
//}
