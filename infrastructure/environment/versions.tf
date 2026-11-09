terraform {
  required_version = "1.15.0"
  required_providers {
    archive = {
      source = "hashicorp/archive"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "6.32.1"
    }
    local = {
      source = "hashicorp/local"
    }
    null = {
      source = "hashicorp/null"
    }
  }
}
