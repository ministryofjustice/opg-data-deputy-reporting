data "aws_wafv2_web_acl" "main" {
  name  = "deputy-reporting-web-acl"
  scope = "REGIONAL"
}

resource "aws_wafv2_web_acl_association" "deputy_reporting" {
  resource_arn = module.deploy_v2.stage.arn
  web_acl_arn  = data.aws_wafv2_web_acl.main.arn
}