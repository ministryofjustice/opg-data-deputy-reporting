terraform {
  required_version = "1.8.1"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.45.0"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}
