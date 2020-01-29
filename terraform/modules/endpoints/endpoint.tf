//-------------------------------------
// Configure the endpoint's permissions

// Allow the endpoint to invoke the lambda.

# Defines products that have access to endpoint on the Gateway

// -----------------------------------------------------------
//DIGIDEPS
//
resource "aws_iam_role" "digideps_tool_role" {
  name               = "sirius-api-gateway-access"
  assume_role_policy = data.aws_iam_policy_document.digideps_role_cross_account_api.json
}

// Access policy, defining who and assume this role
data "aws_iam_policy_document" "digideps_role_cross_account_api" {
  statement {
    sid = "CrossAccountApiGatewayAccessPolicy"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type = "AWS"

      identifiers = [
        local.api_gateway_allowed_users
      ]
    }
  }
}
//
//resource "aws_iam_role_policy_attachment" "digideps_get_lpas_id_access_policy" {
//  role       = "${aws_iam_role.digideps_tool_role.name}"
//  policy_arn = "${module.lpa_online_tool_get_lpas_id.access_policy_arn}"  //api collections gateway
//}
//
//
//
//
//
//
//////------------------------------------
////// Stage level settings
////
//resource "aws_api_gateway_method_settings" "global_gateway_settings" {
//  rest_api_id = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
//  stage_name  = "${aws_api_gateway_deployment.deployment_v1.stage_name}"
//  method_path = "*/*"
//
//  settings {
//    metrics_enabled = true
//    logging_level   = "INFO"
//  }
//}
//
//resource "aws_api_gateway_domain_name" "opg_api_gateway" {
//  domain_name              = "api.${local.opg_sirius_hosted_zone}"
//  regional_certificate_arn = "${data.aws_acm_certificate.sirius_opg_digital.arn}"
//
//  endpoint_configuration {
//    types = ["REGIONAL"]
//  }
//}
//
//resource "aws_api_gateway_base_path_mapping" "mapping" {
//  api_id      = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
//  stage_name  = "${aws_api_gateway_deployment.deployment_v1.stage_name}"
//  domain_name = "${aws_api_gateway_domain_name.opg_api_gateway.domain_name}"
//  base_path   = "${aws_api_gateway_deployment.deployment_v1.stage_name}"
//}
//
//data "aws_route53_zone" "sirius_opg_digital" {
//  name = "${local.opg_sirius_hosted_zone}."
//}
//
//data "aws_acm_certificate" "sirius_opg_digital" {
//  domain      = "*.${local.opg_sirius_hosted_zone}"
//  types       = ["AMAZON_ISSUED"]
//  most_recent = true
//}
//
//resource "aws_route53_record" "opg_api_gateway" {
//  name    = "api.${local.opg_sirius_hosted_zone}"
//  type    = "A"
//  zone_id = "${data.aws_route53_zone.sirius_opg_digital.id}"
//
//  alias {
//    evaluate_target_health = true
//    name                   = "${aws_api_gateway_domain_name.opg_api_gateway.regional_domain_name}"
//    zone_id                = "${aws_api_gateway_domain_name.opg_api_gateway.regional_zone_id}"
//  }
//}
