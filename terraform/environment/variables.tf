variable "default_role" {
  default = "integrations-ci"
}

variable "management_role" {
  default = "integrations-ci"
}

variable "image_tag" {
  default = "latest"
}

variable "use_mock_sirius" {
  default = "0"
  type    = string
}

variable "accounts" {
  type = map(
    object({
      account_id           = string
      account_mapping      = string
      allowed_roles        = list(string)
      digideps_account_id  = string
      digideps_bucket_name = string
      is_production        = string
      logger_level         = string
      opg_hosted_zone      = string
      vpc_id               = string
      session_data         = string
      target_environment   = string
      threshold            = number
      s3_vpc_endpoint_ids  = set(string)
    })
  )
}
