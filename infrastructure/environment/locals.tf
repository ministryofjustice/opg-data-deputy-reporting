locals {
  environment       = terraform.workspace
  account           = contains(keys(var.accounts), local.environment) ? var.accounts[local.environment] : var.accounts.development
  branch_build_flag = contains(keys(var.accounts), local.environment) ? false : true
  a_record          = local.branch_build_flag ? "${local.environment}.${data.aws_route53_zone.environment_cert.name}" : data.aws_route53_zone.environment_cert.name
  service           = "Deputy Reporting Integration"

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
    region        = "eu-west-1"
    environment   = local.environment
    account_id    = local.account.account_id
    allowed_roles = join(", ", local.account.allowed_roles)
  }

  threshold_alert_std   = terraform.workspace == "production" ? 1 : 100
  threshold_alert_4xx   = terraform.workspace == "production" ? 1 : 100
  threshold_alert_count = terraform.workspace == "production" ? 150 : 500

  target_environment = local.account.target_environment
  //Modify here for new version
  latest_openapi_version = "v2"
  openapispec            = "../../lambda_functions/${local.latest_openapi_version}/openapi/${local.api_name}-openapi.yml"
}

output "rest_arn" {
  value = aws_api_gateway_rest_api.deputy_reporting.execution_arn
}
