terraform {
  required_version = "1.11.2"
  required_providers {
    archive = {
      source = "hashicorp/archive"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "5.91.0"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}
