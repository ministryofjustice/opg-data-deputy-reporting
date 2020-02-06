//===============Related to Task Execution Role===================

//This is the role that gets assumed from ECS task with assume_role attached
resource "aws_iam_role" "data_deputy_reporting" {
  name               = "digital-deputy-api-gateway-access-${var.environment}"
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
      identifiers = var.deputy_reporting_api_gateway_allowed_roles
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
      "${var.deputy_reporting_api_gateway.execution_arn}/*/*/${var.resource_part_1}*",
    ]
  }
}

//Name of policies and the attachment
resource "aws_iam_policy" "access_policy" {
  depends_on = [aws_api_gateway_integration.integration]

  name   = "${var.resource_part_1}_${var.resource_part_2}_access_policy_${var.environment}"
  policy = data.aws_iam_policy_document.gateway_resource_execution_policy.json
}

//aws_iam_role_policy_attachment.access_policy_attachment gets called from outside
//to make act as a depedency for deployment

//==================================

//This is directly applied on lambda
resource "aws_lambda_permission" "gateway_lambda_permission" {
  depends_on    = [local.resource_id]
  statement_id  = "AllowApiDeputyReportingGatewayInvoke_${var.resource_part_1}_${var.resource_part_2}_${var.environment}"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${var.deputy_reporting_api_gateway.execution_arn}/*/${aws_api_gateway_method.get[0].http_method}/${var.resource_part_1}*"
}
