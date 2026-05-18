terraform {
  required_version = "1.14.4"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.100.0"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}
