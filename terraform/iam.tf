//This gets attached on the deputy_reporting_api_gateway directly (api_rest.tf)
data "aws_iam_policy_document" "resource_policy" {
  statement {
    sid    = "ApiAllowDigitalDeputyUsers"
    effect = "Allow"

    principals {
      identifiers = local.deputy_reporting_api_gateway_allowed_roles
      type        = "AWS"
    }

    actions = ["execute-api:Invoke"]

    // API Gateway will add all of the rest of the ARN details in for us. Provents a circular dependency.
    resources = ["execute-api:/*/GET/digital-deputy/*"]
  }
}
