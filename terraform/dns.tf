//===== Reference Zones from management =====

data "aws_route53_zone" "opg_env_zone" {
  name     = "${local.account["opg_hosted_zone"]}."
  provider = aws.management
}

//===== Create certificates for sub domains =====

resource "aws_acm_certificate" "opg_env_cert" {
  domain_name               = "*.${data.aws_route53_zone.opg_env_zone.name}"
  validation_method         = "DNS"
  subject_alternative_names = [data.aws_route53_zone.opg_env_zone.name]
  count                     = local.branch_build_flag ? 0 : 1
  lifecycle {
    create_before_destroy = true
  }
}

data "aws_acm_certificate" "opg_env_cert" {
  domain      = "*.${trimsuffix(data.aws_route53_zone.opg_env_zone.name, ".")}"
  types       = ["AMAZON_ISSUED"]
  most_recent = true
  count       = local.branch_build_flag ? 1 : 0
}

resource "aws_route53_record" "opg_validation" {
  name     = aws_acm_certificate.opg_env_cert[0].domain_validation_options[0].resource_record_name
  type     = aws_acm_certificate.opg_env_cert[0].domain_validation_options[0].resource_record_type
  zone_id  = data.aws_route53_zone.opg_env_zone.id
  records  = [aws_acm_certificate.opg_env_cert[0].domain_validation_options[0].resource_record_value]
  ttl      = 60
  provider = aws.management
  count    = local.branch_build_flag ? 0 : 1
}

//===== Create A records =====

resource "aws_route53_record" "opg_env_a_record" {
  name     = local.a_record
  type     = "A"
  zone_id  = data.aws_route53_zone.opg_env_zone.id
  provider = aws.management

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.sirius_deputy_reporting.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.sirius_deputy_reporting.regional_zone_id
  }
}
