terraform {
  required_version = ">= 1.0.0"
  required_providers {
    archive = {
      source = "hashicorp/archive"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "4.16.0"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}
