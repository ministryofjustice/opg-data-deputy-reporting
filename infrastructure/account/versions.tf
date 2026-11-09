terraform {
  required_version = "1.15.0"
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
