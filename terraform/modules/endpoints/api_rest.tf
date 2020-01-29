resource "aws_api_gateway_rest_api" "opg_deputy_reporting_api_gateway" {
  name        = "api-gateway-${terraform.workspace}"
  description = "API Gateway - ${terraform.workspace}"
  policy      = data.aws_iam_policy_document.resource_policy.json

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

data "aws_iam_policy_document" "resource_policy" {
  statement {
    sid    = "digidepsaccess"
    effect = "Allow"

    principals {
      identifiers = var.deputy_reporting_api_gateway_allowed_roles

      type = "AWS"
    }

    actions = ["execute-api:Invoke"]

    // API Gateway will add all of the rest of the ARN details in for us. Provents a circular dependency.
    resources = ["execute-api:/*/GET/deputy-reporting/*"]
  }
}

