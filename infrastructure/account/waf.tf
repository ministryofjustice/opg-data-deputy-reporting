resource "aws_wafv2_web_acl" "deputy_reporting" {
  name        = "deputy-reporting-web-acl"
  description = "Managed rules"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 0

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "SizeRestrictions_BODY"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "CrossSiteScripting_BODY"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "GenericLFI_BODY"
        }
        dynamic "rule_action_override" {
          for_each = [1]
          content {
            action_to_use {
              count {}
            }
            name = "NoUserAgent_HEADER"
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }
  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }
  rule {
    name     = "AWS-AWSManagedRulesPHPRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesPHPRuleSet"
        vendor_name = "AWS"
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "PHPHighRiskMethodsVariables_BODY"
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesPHPRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Rule to allow requests to specific URIs
  rule {
    name     = "AllowRequestsToSpecificURIsFromHost"
    priority = 3

    action {
      allow {}
    }

    statement {
      and_statement {
        statement {
          # Check if the request is from the specific host
          byte_match_statement {
            search_string = "ddls319243.dev.deputy-reporting.api.opg.service.justice.gov.uk"
            field_to_match {
              single_header {
                name = "host"
              }
            }
            positional_constraint = "EXACTLY"
            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }

        statement {
          # Check if the URI path matches one of the allowed regex patterns
          regex_pattern_set_reference_statement {
            arn = aws_wafv2_regex_pattern_set.allow_uris.arn
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AllowRequestsToSpecificURIsFromHost"
      sampled_requests_enabled   = true
    }
  }

  # Rule to block all other requests from the specific host
  rule {
    name     = "BlockAllOtherRequestsFromHost"
    priority = 4

    action {
      block {}
    }

    statement {
      byte_match_statement {
        search_string = "ddls319243.dev.deputy-reporting.api.opg.service.justice.gov.uk"
        field_to_match {
          single_header {
            name = "host"
          }
        }
        positional_constraint = "EXACTLY"
        text_transformation {
          priority = 0
          type     = "NONE"
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "BlockAllOtherRequestsFromHost"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "deputy-reporting-web-acl"
    sampled_requests_enabled   = true
  }
}

resource "aws_cloudwatch_log_group" "waf_deputy_reporting" {
  name              = "aws-waf-logs-deputy-reporting"
  retention_in_days = 7
  tags = {
    "Name" = "aws-waf-logs-deputy-reporting"
  }
}

resource "aws_wafv2_web_acl_logging_configuration" "sirius" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_deputy_reporting.arn]
  resource_arn            = aws_wafv2_web_acl.deputy_reporting.arn
}




resource "aws_wafv2_regex_pattern_set" "allow_uris" {
  name        = "deputy-reporting-allow-uris"
  description = "Regex pattern set for allowing specific public URIs"

  regular_expression {
    regex_string = "^/v2/clients/.*/reports/.*/checklists/.*$"
  }

  regular_expression {
    regex_string = "^/v2/clients/.*/reports/.*/supportingdocuments$"
  }

  regular_expression {
    regex_string = "^/v2/clients/.*/reports$"
  }

  regular_expression {
    regex_string = "^/v2/clients/.*/reports/.*/checklists$"
  }

  regular_expression {
    regex_string = "^/v2/healthcheck$"
  }

  scope = "REGIONAL"
}
