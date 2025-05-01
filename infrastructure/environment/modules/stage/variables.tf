variable "account_name" {}

variable "api_name" {}

variable "aws_subnet_ids" {
  type = list(string)
}

variable "content_api_sha" {
  description = "SHA for the content of the openapi spec"
  type        = string
}

variable "content_api_gateway_policy_sha" {
  description = "SHA for the content of the API Gateway Policy"
  type        = string
}

variable "domain_name" {}
variable "environment" {
  type = string
}

variable "flaskapp_lambda" {}

variable "openapi_version" {}

variable "region_name" {}

variable "rest_api" {}

variable "tags" {}

variable "target_environment" {
  type = string
}

variable "vpc_id" {
  type = string
}
