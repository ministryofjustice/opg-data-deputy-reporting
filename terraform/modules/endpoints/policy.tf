resource "aws_lambda_permission" "gateway_lambda_permission" {
  depends_on = [aws_api_gateway_resource.gateway_resource_collection]

  statement_id  = "AllowOpgApiGatewayInvoke_${var.gateway_path_product}_${var.gateway_path_collection}_id"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.opg_deputy_reporting_api_gateway.execution_arn}/*/${aws_api_gateway_method.gateway_resource_collection_get.http_method}${aws_api_gateway_resource.gateway_resource_collection.path}"
}

//-------------------------------------
// Configure the endpoint's access policy
// i.e. who can access the endpoint
// Generate a policy that allowed the endpoint to be called from a user/group/role.
data "aws_iam_policy_document" "gateway_resource_execution_policy" {
  statement {
    sid = "OPGApiGatewayAccessPolicy"

    actions = [
      "execute-api:Invoke",
    ]

    resources = [
      "${aws_api_gateway_rest_api.opg_deputy_reporting_api_gateway.execution_arn}/*/*${aws_api_gateway_resource.gateway_resource_product.path}/*",
    ]
  }
}

resource "aws_iam_policy" "opg_api_gateway_access_policy" {
  depends_on = [aws_api_gateway_integration.gateway_digideps_collection_resource_get_integration]

  name   = "${var.gateway_path_product}_${var.gateway_path_collection}_access_policy"
  path   = "/"
  policy = data.aws_iam_policy_document.gateway_resource_execution_policy.json
}