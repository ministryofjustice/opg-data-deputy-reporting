terraform {
  required_version = "1.11.3"
  required_providers {
    archive = {
      source = "hashicorp/archive"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "5.94.0"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}
