locals {
  //Modify here for new version
  v2 = {
    flask_app_name : var.flaskapp_lambda.function_name
  }
  stage_vars = local.v2
}

resource "aws_api_gateway_stage" "currentstage" {
  stage_name           = var.openapi_version
  depends_on           = [aws_cloudwatch_log_group.deputy_reporting]
  rest_api_id          = var.rest_api.id
  deployment_id        = aws_api_gateway_deployment.deploy.id
  xray_tracing_enabled = false
  tags                 = var.tags
  //Modify here for new version
  //variables = local.v1
  variables = local.stage_vars

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.deputy_reporting.arn
    format = join("", [
      "{\"requestId\":\"$context.requestId\",",
      "\"ip\":\"$context.identity.sourceIp\",",
      "\"caller\":\"$context.identity.caller\",",
      "\"user\":\"$context.identity.user\",",
      "\"requestTime\":\"$context.requestTime\",",
      "\"httpMethod\":\"$context.httpMethod\",",
      "\"resourcePath\":\"$context.resourcePath\",",
      "\"status\":\"$context.status\",",
      "\"protocol\":\"$context.protocol\",",
      "\"responseLength\":\"$context.responseLength\"}"
    ])
  }
}

resource "aws_cloudwatch_log_group" "deputy_reporting" {
  name              = "API-Gateway-Execution-Logs-${var.rest_api.name}-${var.openapi_version}"
  retention_in_days = 30
  tags              = var.tags
}


data "aws_wafv2_web_acl" "integrations" {
  name  = "integrations-${var.account_name}-${var.region_name}-web-acl"
  scope = "REGIONAL"
}

resource "aws_wafv2_web_acl_association" "api_gateway_stage" {
  resource_arn = aws_api_gateway_stage.currentstage.arn
  web_acl_arn  = data.aws_wafv2_web_acl.integrations.arn
}
