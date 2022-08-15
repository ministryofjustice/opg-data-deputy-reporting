//===============Related to Task Execution Role===================

//This is the role that gets assumed from ECS task with assume_role attached
resource "aws_iam_role" "data_deputy_reporting" {
  name               = "digital-deputy-api-gateway-access-${local.environment}"
  assume_role_policy = data.aws_iam_policy_document.cross_account_api.json
}

// Access policy, defining who can assume this role
data "aws_iam_policy_document" "cross_account_api" {
  statement {
    sid = "CrossAccountApiGatewayAccessPolicy"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type        = "AWS"
      identifiers = local.account.allowed_roles
    }
  }
}

//Access policy allowing execute on the particular api gateway endpoint
data "aws_iam_policy_document" "gateway_resource_execution_policy" {
  statement {
    sid = "ApiDeputyReportingGatewayAccessPolicy"

    actions = [
      "execute-api:Invoke",
    ]

    resources = [
      "${aws_api_gateway_rest_api.deputy_reporting.execution_arn}/*/*/*",
    ]
  }
}

//Name of policies and the attachment
resource "aws_iam_policy" "access_policy" {
  depends_on = [aws_api_gateway_rest_api.deputy_reporting]

  name   = "access-policy-${local.environment}"
  policy = data.aws_iam_policy_document.gateway_resource_execution_policy.json
}

resource "aws_iam_role_policy_attachment" "access_policy_attachment" {
  role       = aws_iam_role.data_deputy_reporting.id
  policy_arn = aws_iam_policy.access_policy.arn
}
