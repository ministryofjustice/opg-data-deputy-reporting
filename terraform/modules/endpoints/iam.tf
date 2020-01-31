//===============Related to data_deputy_reporting role===================

//This is the role that gets assumed from ECS task with assume_role attached
resource "aws_iam_role" "data_deputy_reporting" {
  name               = "digital-deputy-api-gateway-access"
  assume_role_policy = data.aws_iam_policy_document.deputy_reporting_role_cross_account_api.json
}

// Access policy, defining who can assume this role
data "aws_iam_policy_document" "deputy_reporting_role_cross_account_api" {
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
      "${var.deputy_reporting_api_gateway.execution_arn}/*/*${aws_api_gateway_resource.gateway_resource_product.path}/*",
    ]
  }
}

//Name of policies and the attachment
resource "aws_iam_policy" "deputy_reporting_access_policy" {
  depends_on = [aws_api_gateway_integration.gateway_deputy_reporting_collection_resource_get_integration]

  name   = "${var.gateway_path_product}_${var.gateway_path_collection}_access_policy"
  policy = data.aws_iam_policy_document.gateway_resource_execution_policy.json
}

//THIS GETS CALLED FROM OUTSIDE
//resource "aws_iam_role_policy_attachment" "deputy_reporting_access_policy_attachment" {
//  role       = aws_iam_role.data_deputy_reporting.name
//  policy_arn = aws_iam_policy.deputy_reporting_access_policy.arn  //api collections gateway
//}

//==================================

//This is directly applied on lambda
resource "aws_lambda_permission" "gateway_lambda_permission" {
  depends_on = [aws_api_gateway_resource.gateway_resource_collection]

  statement_id  = "AllowApiDeputyReportingGatewayInvoke_${var.gateway_path_product}_${var.gateway_path_collection}_id"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path within API Gateway REST API.
  //LOCK THIS DOWN
  source_arn = "${var.deputy_reporting_api_gateway.execution_arn}/*/${aws_api_gateway_method.gateway_resource_collection_get.http_method}${aws_api_gateway_resource.gateway_resource_collection.path}"
}


