terraform {
  required_version = "1.14.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.26.0"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}
