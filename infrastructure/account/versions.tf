terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.25.0"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}