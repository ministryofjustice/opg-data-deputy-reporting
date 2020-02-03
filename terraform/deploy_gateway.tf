resource "aws_api_gateway_deployment" "deployment_v1" {
  rest_api_id = aws_api_gateway_rest_api.deputy_reporting_api_gateway.id
  stage_name  = "v1"

  // The policy is dependent on the module completing, so we can depend on that to mean everything is in place
  depends_on = [aws_iam_role_policy_attachment.deputy_reporting_access_policy_attachment]

  variables = {
    // Force a deploy on every apply.
    deployed_at = timestamp()
  }

  lifecycle {
    create_before_destroy = true
  }
}
