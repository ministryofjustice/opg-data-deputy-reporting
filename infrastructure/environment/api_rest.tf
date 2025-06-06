resource "aws_api_gateway_rest_api" "deputy_reporting" {
  name        = "deputy-reporting-${local.environment}"
  description = "API Gateway for Deputy Reporting - ${local.environment}"
  body        = local.template_file
  policy      = sensitive(data.aws_iam_policy_document.deputy_reporting_rest_api_policy.json)
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  # This is important to manage the update of roles form openapi spec properly
  lifecycle {
    replace_triggered_by = [null_resource.api_gateway]
  }
  tags = local.default_tags
}

resource "null_resource" "api_gateway" {
  triggers = {
    open_api_sha        = local.open_api_sha
    rest_api_policy_sha = local.rest_api_policy_sha
  }
}

locals {
  template_file       = templatefile(local.openapispec, local.api_template_vars)
  open_api_sha        = substr(replace(base64sha256(local.template_file), "/[^0-9A-Za-z_]/", ""), 0, 5)
  rest_api_policy_sha = substr(base64sha256(data.aws_iam_policy_document.deputy_reporting_rest_api_policy.json), 0, 5)
}

data "aws_iam_policy_document" "deputy_reporting_rest_api_policy" {
  override_policy_documents = local.ip_restrictions_enabled ? [data.aws_iam_policy_document.deputy_reporting_rest_api_ip_restriction_policy[0].json] : []
  statement {
    sid    = "AllowExecuteByAllowedRoles"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = local.account.allowed_roles
    }
    actions   = ["execute-api:Invoke"]
    resources = ["arn:aws:execute-api:eu-west-?:${local.account.account_id}:*/*/*/*"]
  }
}
data "aws_iam_policy_document" "deputy_reporting_rest_api_ip_restriction_policy" {
  count = local.ip_restrictions_enabled ? 1 : 0
  statement {
    sid    = "DenyExecuteByNoneAllowedIPRanges"
    effect = "Deny"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions       = ["execute-api:Invoke"]
    not_resources = ["arn:aws:execute-api:eu-west-?:${local.account.account_id}:*/*/*/healthcheck"]
    condition {
      test     = "NotIpAddress"
      variable = "aws:SourceIp"
      values   = sensitive(local.allow_list_mapping[local.account.account_mapping])
    }
  }
}

module "allow_list" {
  source = "git@github.com:ministryofjustice/opg-terraform-aws-moj-ip-allow-list.git?ref=v3.3.0"
}

locals {
  allow_list_mapping = {
    development = concat(
      module.allow_list.sirius_dev_allow_list,
      module.allow_list.digideps_development,
    )
    preproduction = concat(
      module.allow_list.sirius_pre_allow_list,
      module.allow_list.digideps_preproduction,
    )
    production = concat(
      module.allow_list.sirius_prod_allow_list,
      module.allow_list.digideps_production
    )
  }
  ip_restrictions_enabled = contains(["preproduction"], local.account.account_mapping)
}
