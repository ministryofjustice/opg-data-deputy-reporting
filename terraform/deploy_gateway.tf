resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = aws_api_gateway_rest_api.deputy_reporting_api_gateway.id
  depends_on  = [aws_api_gateway_domain_name.sirius_deputy_reporting]
  variables = {
    // Force a deploy on every apply.
    deployed_at = timestamp()
  }

  lifecycle {
    create_before_destroy = true
  }
}
