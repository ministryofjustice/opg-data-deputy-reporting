resource "aws_api_gateway_method_settings" "global_gateway_settings" {
  rest_api_id = aws_api_gateway_rest_api.deputy_reporting_api_gateway.id
  stage_name  = aws_api_gateway_deployment.deployment_v1.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}

resource "aws_api_gateway_domain_name" "sirius_deputy_reporting" {
  domain_name              = "api-deputy-reporting.${local.account["sirius_hosted_zone"]}"
  regional_certificate_arn = data.aws_acm_certificate.sirius.arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_base_path_mapping" "mapping" {
  api_id      = aws_api_gateway_rest_api.deputy_reporting_api_gateway.id
  stage_name  = aws_api_gateway_deployment.deployment_v1.stage_name
  domain_name = aws_api_gateway_domain_name.sirius_deputy_reporting.domain_name
  base_path   = aws_api_gateway_deployment.deployment_v1.stage_name
}
