resource "aws_api_gateway_stage" "currentstage" {
  stage_name           = var.openapi_version
  depends_on           = [aws_cloudwatch_log_group.deputy_reporting]
  rest_api_id          = var.rest_api.id
  deployment_id        = aws_api_gateway_deployment.deploy.id
  xray_tracing_enabled = true
  tags                 = var.tags
  variables = {
    healthcheck_function_name : var.healthcheck_lambda.function_name
    reports_function_name : var.reports_lambda.function_name
    supporting_docs_name : var.supportingdocs_lambda.function_name
    checklists_name : var.checklists_lambda.function_name
  }

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.deputy_reporting.arn
    format = join("", [
      "{\"requestId\":\"$context.requestId\",",
      "\"ip\":\"$context.identity.sourceIp\"",
      "\"caller\":\"$context.identity.caller\"",
      "\"user\":\"$context.identity.user\"",
      "\"requestTime\":\"$context.requestTime\"",
      "\"httpMethod\":\"$context.httpMethod\"",
      "\"resourcePath\":\"$context.resourcePath\"",
      "\"status\":\"$context.status\"",
      "\"protocol\":\"$context.protocol\"",
      "\"responseLength\":\"$context.responseLength\"}"
    ])
  }
}

resource "aws_cloudwatch_log_group" "deputy_reporting" {
  name              = "API-Gateway-Execution-Logs-${var.rest_api.name}-${var.openapi_version}"
  retention_in_days = 30
  tags              = var.tags
}
