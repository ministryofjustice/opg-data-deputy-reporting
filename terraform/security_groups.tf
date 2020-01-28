resource "aws_security_group" "lambda_egress" {
  name_prefix = "opg-data-deputy-reporting-lambda-egress-${local.environment}-"
  description = "egress rules for OPG Sirius API Gateway"
  vpc_id      = local.account["vpc_id"]
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "global_egress" {
  from_port         = 0
  protocol          = "-1"
  security_group_id = aws_security_group.lambda_egress.id
  to_port           = 0
  type              = "egress"
  cidr_blocks       = ["0.0.0.0/0"]
}

data "aws_security_group" "lambda_api_ingress" {
  filter {
    name   = "tag:Name"
    values = ["integration-lambda-api-access-${local.account["target_environment"]}"]
  }
}
