locals {
  environment = terraform.workspace
  account     = contains(keys(var.accounts), local.environment) ? var.accounts[local.environment] : var.accounts["development"]

  sirius_hosted_zones = {
    "development" = "dev.sirius.opg.digital"
    "production"  = "sirius.opg.digital"
  }

  sirius_hosted_zone = lookup(local.sirius_hosted_zones, terraform.workspace)

  deputy_reporting_development_api_gateway_allowed_roles = [
    "arn:aws:iam::248804316466:root",
  ]

  deputy_reporting_production_api_gateway_allowed_roles = [
    "arn:aws:iam::454262938596:role/api_task",
    "arn:aws:iam::515688267891:role/api_task",
  ]
  deputy_reporting_api_gateway_allowed_roles = split(",", terraform.workspace == "development" ? join(",", local.deputy_reporting_development_api_gateway_allowed_roles) : join(",", local.deputy_reporting_production_api_gateway_allowed_roles))
}


