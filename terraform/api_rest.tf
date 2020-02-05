resource "aws_api_gateway_rest_api" "deputy_reporting_api_gateway" {
  name        = "deputy-reporting-${terraform.workspace}"
  description = "API Gateway for Deputy Reporting - ${terraform.workspace}"
  policy      = data.aws_iam_policy_document.resource_policy.json

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}
