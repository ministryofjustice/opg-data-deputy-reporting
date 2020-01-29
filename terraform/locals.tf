locals {
  environment = terraform.workspace
  account     = contains(keys(var.accounts), local.environment) ? var.accounts[local.environment] : var.accounts["development"]

  deputy_reporting_development_api_gateway_allowed_roles = [
    "arn:aws:iam::001780581745:root",
    "arn:aws:iam::050256574573:root",
  ]

  deputy_reporting_production_api_gateway_allowed_roles = [
    "arn:aws:iam::987830934591:role/preproduction-api-task-role",
    "arn:aws:iam::980242665824:role/production-api-task-role",
  ]
  deputy_reporting_api_gateway_allowed_roles = split(",", terraform.workspace == "development" ? join(",", local.deputy_reporting_development_api_gateway_allowed_roles) : join(",", local.deputy_reporting_production_api_gateway_allowed_roles))
}


