locals {
  certificate_arn = local.branch_build_flag ? data.aws_acm_certificate.environment_cert[0].arn : aws_acm_certificate.environment_cert[0].arn
  certificate     = local.branch_build_flag ? data.aws_acm_certificate.environment_cert[0] : aws_acm_certificate.environment_cert[0]
}

resource "aws_api_gateway_method_settings" "global_gateway_settings" {
  rest_api_id = aws_api_gateway_rest_api.deputy_reporting.id
  //Modify here for new version
  stage_name  = module.deploy_v2.stage.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }

}

resource "aws_api_gateway_domain_name" "sirius_deputy_reporting" {
  domain_name              = trimsuffix(local.a_record, ".")
  regional_certificate_arn = local.certificate_arn
  security_policy          = "TLS_1_2"

  depends_on = [local.certificate]
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = local.default_tags
}

//Modify here for new version
module "deploy_v2" {
  source                         = "./modules/stage"
  account_name                   = local.account.account_mapping
  api_name                       = local.api_name
  aws_subnet_ids                 = data.aws_subnets.private.ids
  content_api_sha                = local.open_api_sha
  content_api_gateway_policy_sha = local.rest_api_policy_sha
  domain_name                    = aws_api_gateway_domain_name.sirius_deputy_reporting
  environment                    = local.environment
  flaskapp_lambda                = module.lamdba_flask_v2.lambda
  openapi_version                = "v2"
  region_name                    = data.aws_region.region.region
  rest_api                       = aws_api_gateway_rest_api.deputy_reporting
  tags                           = local.default_tags
  target_environment             = local.target_environment
  vpc_id                         = local.account.vpc_id
}

//To Add New Version Copy and Paste Above and Modify Accordingly
//Below takes the latest stage/deployment. Modify for new version.

//Modify here for new version
resource "aws_api_gateway_base_path_mapping" "mapping_v2" {
  api_id      = aws_api_gateway_rest_api.deputy_reporting.id
  stage_name  = module.deploy_v2.stage.stage_name
  domain_name = aws_api_gateway_domain_name.sirius_deputy_reporting.domain_name
  base_path   = module.deploy_v2.stage.stage_name
}
