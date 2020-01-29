variable "gateway_path_product" {
  type = string
}

variable "gateway_path_collection" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "region" {
  type = string
}

variable "deputy_reporting_api_gateway_allowed_roles" {
  type = list(string)
}

variable "lambda_arn" {
  type = string
}