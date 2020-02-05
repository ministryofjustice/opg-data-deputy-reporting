locals {
  environment = terraform.workspace
  account     = contains(keys(var.accounts), local.environment) ? var.accounts[local.environment] : var.accounts["development"]

  deputy_reporting_development_api_gateway_allowed_roles = [
    "arn:aws:iam::248804316466:root", //This needs to be root as we are doing branch based dev with different task roles
  ]

  deputy_reporting_production_api_gateway_allowed_roles = [
    "arn:aws:iam::454262938596:role/api_task_name_not_defined_yet",
    "arn:aws:iam::515688267891:role/api_task_name_not_defined_yet",
  ]
  deputy_reporting_api_gateway_allowed_roles = split(",", terraform.workspace == "development" ? join(",", local.deputy_reporting_development_api_gateway_allowed_roles) : join(",", local.deputy_reporting_production_api_gateway_allowed_roles))
}
