locals {
  resource_id = var.resource_part_3 != "" ? aws_api_gateway_resource.path_part_3[0].id : (var.resource_part_2 != "" ? aws_api_gateway_resource.path_part_2[0].id : aws_api_gateway_resource.path_part_1[0].id)
}

resource "aws_api_gateway_resource" "path_part_1" {
  rest_api_id = var.deputy_reporting_api_gateway.id
  parent_id   = var.deputy_reporting_api_gateway.root_resource_id
  count       = var.resource_part_1 == "" ? 0 : 1
  path_part   = var.resource_part_1
}

resource "aws_api_gateway_resource" "path_part_2" {
  rest_api_id = var.deputy_reporting_api_gateway.id
  parent_id   = aws_api_gateway_resource.path_part_1[0].id
  count       = var.resource_part_2 == "" ? 0 : 1
  path_part   = var.resource_part_2
}

resource "aws_api_gateway_resource" "path_part_3" {
  rest_api_id = var.deputy_reporting_api_gateway.id
  parent_id   = aws_api_gateway_resource.path_part_2[0].id
  count       = var.resource_part_3 == "" ? 0 : 1
  path_part   = var.resource_part_3
}

//-------------------------------------
// Setup the method

resource "aws_api_gateway_method" "get" {
  rest_api_id   = var.deputy_reporting_api_gateway.id
  resource_id   = local.resource_id
  count         = var.method == "GET" ? 1 : 0
  http_method   = "GET"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_method" "post" {
  rest_api_id   = var.deputy_reporting_api_gateway.id
  resource_id   = local.resource_id
  count         = var.method == "POST" ? 1 : 0
  http_method   = "POST"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = var.deputy_reporting_api_gateway.id
  resource_id             = local.resource_id
  http_method             = var.method == "GET" ? aws_api_gateway_method.get[0].http_method : aws_api_gateway_method.post[0].http_method
  integration_http_method = "POST" # We POST to Lambda, even on a HTTP GET.

  type             = "AWS_PROXY"
  content_handling = "CONVERT_TO_TEXT"

  uri = var.lambda.invoke_arn
}
