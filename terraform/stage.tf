locals {
  certificate_arn = local.branch_build_flag ? data.aws_acm_certificate.environment_cert[0].arn : aws_acm_certificate.environment_cert[0].arn
  certificate     = local.branch_build_flag ? data.aws_acm_certificate.environment_cert[0] : aws_acm_certificate.environment_cert[0]
}

resource "aws_api_gateway_method_settings" "global_gateway_settings" {
  rest_api_id = aws_api_gateway_rest_api.deputy_reporting_api_gateway.id
  stage_name  = aws_api_gateway_stage.currentstage.stage_name
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

resource "aws_api_gateway_stage" "currentstage" {
  stage_name           = var.stage
  depends_on           = [aws_cloudwatch_log_group.deputy_reporting]
  rest_api_id          = aws_api_gateway_rest_api.deputy_reporting_api_gateway.id
  deployment_id        = aws_api_gateway_deployment.deploy.id
  xray_tracing_enabled = true
  tags                 = local.default_tags
}

resource "aws_api_gateway_base_path_mapping" "mapping" {
  api_id      = aws_api_gateway_rest_api.deputy_reporting_api_gateway.id
  stage_name  = aws_api_gateway_deployment.deploy.stage_name
  domain_name = aws_api_gateway_domain_name.sirius_deputy_reporting.domain_name
  base_path   = aws_api_gateway_deployment.deploy.stage_name
}

resource "aws_cloudwatch_log_group" "deputy_reporting" {
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.deputy_reporting_api_gateway.id}"
  retention_in_days = 7
  tags              = local.default_tags
}
