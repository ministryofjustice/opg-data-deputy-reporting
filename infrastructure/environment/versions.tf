terraform {
  required_version = "1.11.2"
  required_providers {
    archive = {
      source = "hashicorp/archive"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "5.92.0"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}
