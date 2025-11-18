terraform {
  backend "s3" {
    bucket  = "opg.terraform.state"
    key     = "opg-data-deputy-reporting-account/terraform.tfstate"
    encrypt = true
    region  = "eu-west-1"
    assume_role = {
      role_arn = "arn:aws:iam::311462405659:role/integrations-ci"
    }
    use_lockfile = true
  }
}

provider "aws" {
  region = "eu-west-1"
  default_tags {
    tags = {
      business-unit          = "OPG"
      application            = "Data-Deputy-Reporting"
      environment-name       = local.environment
      owner                  = "OPG Supervision"
      infrastructure-support = "OPG WebOps: opgteam@digital.justice.gov.uk"
      is-production          = local.account.is_production
      source-code            = "https://github.com/ministryofjustice/opg-data-deputy-reporting"
    }
  }
  assume_role {
    role_arn     = "arn:aws:iam::${local.account.account_id}:role/${var.default_role}"
    session_name = "terraform-session"
  }
}

provider "aws" {
  region = "eu-west-1"
  alias  = "management"
  assume_role {
    role_arn     = "arn:aws:iam::311462405659:role/${var.management_role}"
    session_name = "terraform-session"
  }
}
