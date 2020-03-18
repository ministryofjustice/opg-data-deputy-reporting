locals {
  api_name = "deputy-reporting"
  api_template_vars = {
    lambda_reports_arn     = module.lambda_reports.lambda_arn
    lambda_healthcheck_arn = module.lamdba_healthcheck.lambda_arn
    region                 = "eu-west-1"
    environment            = local.environment
  }
  openapispec = file("../../${local.api_name}-openapi.yml")
}

data "template_file" "_" {
  template = local.openapispec
  vars     = local.api_template_vars
}

// Bug - Recreates api gateway spec on each build!
// Can't use Lifecycle ignore changes as not attaching policy on first build!
// https://github.com/terraform-providers/terraform-provider-aws/issues/5549
resource "aws_api_gateway_rest_api" "deputy_reporting_api_gateway" {
  name        = "deputy-reporting-${local.environment}"
  description = "API Gateway for Deputy Reporting - ${local.environment}"
  policy      = data.aws_iam_policy_document.resource_policy.json
  body        = data.template_file._.rendered

  endpoint_configuration {
    types = ["REGIONAL"]
  }
  tags = local.default_tags
}
