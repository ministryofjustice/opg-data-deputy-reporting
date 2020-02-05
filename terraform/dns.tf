data "aws_route53_zone" "sirius" {
  name = "${local.account["sirius_hosted_zone"]}."
}

data "aws_acm_certificate" "sirius" {
  domain      = "*.${local.account["sirius_hosted_zone"]}"
  types       = ["AMAZON_ISSUED"]
  most_recent = true
}

resource "aws_route53_record" "sirius" {
  name    = "api-deputy-reporting.${local.account["sirius_hosted_zone"]}"
  type    = "A"
  zone_id = data.aws_route53_zone.sirius.id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.sirius_deputy_reporting.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.sirius_deputy_reporting.regional_zone_id
  }
}
