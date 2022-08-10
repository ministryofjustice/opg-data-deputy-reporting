variable "default_role" {
  default = "integrations-ci"
}

variable "management_role" {
  default = "integrations-ci"
}

variable "accounts" {
  type = map(
    object({
      account_id    = string
      is_production = string
    })
  )
}
