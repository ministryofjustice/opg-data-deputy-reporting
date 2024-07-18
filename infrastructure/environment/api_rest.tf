data "template_file" "_" {
  template = local.openapispec
  vars     = local.api_template_vars
}

resource "aws_api_gateway_rest_api" "deputy_reporting" {
  name        = "deputy-reporting-${local.environment}"
  description = "API Gateway for Deputy Reporting - ${local.environment}"
  body        = data.template_file._.rendered

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  # This is important to manage the update of roles form openapi spec properly
  lifecycle {
    replace_triggered_by = [
      aws_iam_role.data_deputy_reporting
    ]
  }

  tags = local.default_tags
}
