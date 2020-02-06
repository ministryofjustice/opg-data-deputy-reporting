resource "aws_api_gateway_rest_api" "deputy_reporting_api_gateway" {
  name        = "deputy-reporting-${local.environment}"
  description = "API Gateway for Deputy Reporting - ${local.environment}"
  policy      = data.aws_iam_policy_document.resource_policy.json

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}
