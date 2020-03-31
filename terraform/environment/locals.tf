locals {
  environment       = terraform.workspace
  account           = contains(keys(var.accounts), local.environment) ? var.accounts[local.environment] : var.accounts.development
  branch_build_flag = contains(keys(var.accounts), local.environment) ? false : true
  a_record          = local.branch_build_flag ? "${local.environment}.${data.aws_route53_zone.environment_cert.name}" : data.aws_route53_zone.environment_cert.name

  default_tags = {
    business-unit          = "OPG"
    application            = "Data-Deputy-Reporting"
    environment-name       = local.environment
    owner                  = "OPG Supervision"
    infrastructure-support = "OPG WebOps: opgteam@digital.justice.gov.uk"
    is-production          = local.account.is_production
    source-code            = "https://github.com/ministryofjustice/opg-data-deputy-reporting"
  }

  policy_len_tag = {
    policy_len = aws_api_gateway_rest_api.deputy_reporting.policy
  }

  api_name = "deputy-reporting"

  api_template_vars = {
    region      = "eu-west-1"
    environment = local.environment
    account_id  = local.account.account_id
  }

  //Modify for new version of API
  latest_openapi_version = "1_0_0"
  openapispec            = file("../../${local.api_name}-openapi-${local.latest_openapi_version}.yml")
}

//https://github.com/terraform-providers/terraform-provider-aws/issues/5364
output "policy" {
  value = aws_api_gateway_rest_api.deputy_reporting.policy
}

output "rest_arn" {
  value = aws_api_gateway_rest_api.deputy_reporting.execution_arn
}
