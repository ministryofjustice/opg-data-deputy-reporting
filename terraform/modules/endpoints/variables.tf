variable "lambda" {}

variable "region" {
  type = string
}

variable "deputy_reporting_api_gateway_allowed_roles" {
  type = list(string)
}

variable "deputy_reporting_api_gateway" {}

variable "resource_part_1" {
  type    = string
  default = ""
}

variable "resource_part_2" {
  type    = string
  default = ""
}

variable "resource_part_3" {
  type    = string
  default = ""
}

variable "method" {
  type = string
}
