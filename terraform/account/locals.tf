locals {
  environment = terraform.workspace
  account     = contains(keys(var.accounts), local.environment) ? var.accounts[local.environment] : var.accounts.development

  default_tags = {
    business-unit          = "OPG"
    application            = "Data-Deputy-Reporting"
    environment-name       = local.environment
    owner                  = "OPG Supervision"
    infrastructure-support = "OPG WebOps: opgteam@digital.justice.gov.uk"
    is-production          = local.account.is_production
    source-code            = "https://github.com/ministryofjustice/opg-data-deputy-reporting"
  }
}
