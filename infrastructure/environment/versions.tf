terraform {
  required_version = "1.11.4"
  required_providers {
    archive = {
      source = "hashicorp/archive"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "5.94.1"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}
