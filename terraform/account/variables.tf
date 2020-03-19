variable "default_role" {
  default = "sirius-ci"
}

variable "accounts" {
  type = map(
    object({
      account_id    = string
      is_production = string
    })
  )
}
