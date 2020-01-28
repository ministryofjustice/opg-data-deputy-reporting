variable "default_role" {
  default = "sirius-ci"
}

variable "accounts" {
  type = map(
    object({
      account_id         = string
      account_mapping    = string
      is_production      = string
      target_environment = string
      vpc_id             = string
    })
  )
}

