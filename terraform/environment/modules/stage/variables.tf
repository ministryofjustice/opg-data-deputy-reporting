variable "account_name" {}

variable "api_name" {}

variable "aws_subnet_ids" {
  type = list(string)
}

//THIS IS JUST TEMPORARY
variable "checklists_lambda" {}

variable "domain_name" {}
variable "environment" {
  type = string
}

//THIS IS JUST TEMPORARY
variable "flaskapp_lambda" {}

variable "healthcheck_lambda" {}

variable "openapi_version" {}

variable "region_name" {}

variable "reports_lambda" {}

variable "rest_api" {}

variable "supportingdocs_lambda" {}

variable "tags" {}

variable "target_environment" {
  type = string
}

variable "vpc_id" {
  type = string
}
