resource "aws_api_gateway_resource" "gateway_resource_product" {
  rest_api_id = aws_api_gateway_rest_api.opg_deputy_reporting_api_gateway.id
  parent_id   = aws_api_gateway_rest_api.opg_deputy_reporting_api_gateway.root_resource_id

  path_part = var.gateway_path_product
}

resource "aws_api_gateway_resource" "gateway_resource_collection" {
  rest_api_id = aws_api_gateway_rest_api.opg_deputy_reporting_api_gateway.id
  parent_id   = aws_api_gateway_resource.gateway_resource_product.id

  path_part = var.gateway_path_collection
}

//-------------------------------------
// Setup the method

resource "aws_api_gateway_method" "gateway_resource_collection_get" {
  rest_api_id   = aws_api_gateway_rest_api.opg_deputy_reporting_api_gateway.id
  resource_id   = aws_api_gateway_resource.gateway_resource_product.id
  http_method   = "GET"
  authorization = "AWS_IAM"
}

//-------------------------------------
// Setup the integration

resource "aws_api_gateway_integration" "gateway_digideps_collection_resource_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.opg_deputy_reporting_api_gateway.id
  resource_id             = aws_api_gateway_resource.gateway_resource_collection.id
  http_method             = aws_api_gateway_method.gateway_resource_collection_get.http_method
  integration_http_method = "POST" # We POST to Lambda, even on a HTTP GET.

  type             = "AWS_PROXY"
  content_handling = "CONVERT_TO_TEXT"

  uri = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${var.lambda_arn}/invocations"
}
