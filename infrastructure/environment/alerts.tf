data "aws_sns_topic" "rest_api" {
  name = "rest-api"
}

data "aws_sns_topic" "deputy_reporting_slack" {
  name = "deputy-reporting-slack-alerts"
}

resource "aws_cloudwatch_log_metric_filter" "api_gateway_4xx_errors_specific_uris" {
  name           = "api-gateway-4xx-deputy-reporting-${local.environment}"
  log_group_name = "API-Gateway-Execution-Logs-deputy-reporting-${local.environment}-v2"

  pattern = "{ ($.status = \"4*\") && (($.resourcePath = \"*/clients/*/reports*\") || ($.resourcePath = \"*/healthcheck\")) }"

  metric_transformation {
    name          = "DeputyReporting4xx.${local.environment}"
    namespace     = "Integrations/Error"
    value         = "1"
    default_value = "0"
  }
  depends_on = [module.deploy_v2]
}

resource "aws_cloudwatch_metric_alarm" "rest_api_4xx_errors" {
  actions_enabled = true
  alarm_actions = [
    data.aws_sns_topic.rest_api.arn,
    data.aws_sns_topic.deputy_reporting_slack.arn
  ]
  alarm_name                = "deputy-reporting-${local.environment}-4xx-errors"
  alarm_description         = "SERVICE: ${local.service}`\n`ENVIRONMENT: ${terraform.workspace}`\n`ERROR: 4xx"
  metric_name               = aws_cloudwatch_log_metric_filter.api_gateway_4xx_errors_specific_uris.metric_transformation[0].name
  namespace                 = aws_cloudwatch_log_metric_filter.api_gateway_4xx_errors_specific_uris.metric_transformation[0].namespace
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm       = 1
  evaluation_periods        = 1
  period                    = 60
  threshold                 = local.threshold_alert_std
  statistic                 = "Sum"
  insufficient_data_actions = []
  treat_missing_data        = "notBreaching"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  tags                      = local.default_tags
}

resource "aws_cloudwatch_metric_alarm" "rest_api_5xx_errors" {
  actions_enabled = true
  alarm_actions = [
    data.aws_sns_topic.rest_api.arn,
    data.aws_sns_topic.deputy_reporting_slack.arn
  ]
  alarm_name          = "deputy-reporting-${local.environment}-rest-api-5xx-errors"
  alarm_description   = "SERVICE: ${local.service}`\n`ENVIRONMENT: ${terraform.workspace}`\n`ERROR: 5xx"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm = 3
  dimensions = {
    ApiName = "deputy-reporting-${terraform.workspace}"
  }
  evaluation_periods        = 3
  insufficient_data_actions = []
  metric_name               = "5XXError"
  namespace                 = "AWS/ApiGateway"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.threshold_alert_std
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "rest_api_high_count" {
  actions_enabled = true
  alarm_actions = [
    data.aws_sns_topic.rest_api.arn,
    data.aws_sns_topic.deputy_reporting_slack.arn
  ]
  alarm_name          = "deputy-reporting-${local.environment}-rest-api-high-count"
  alarm_description   = "SERVICE: ${local.service}`\n`ENVIRONMENT: ${terraform.workspace}`\n`ERROR: Abnormally high throughput"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = 1
  dimensions = {
    ApiName = "deputy-reporting-${terraform.workspace}"
  }
  evaluation_periods        = 1
  insufficient_data_actions = []
  metric_name               = "Count"
  namespace                 = "AWS/ApiGateway"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.threshold_alert_count
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_log_metric_filter" "s3_error" {
  name           = "deputy-reporting-s3-error.${local.environment}"
  pattern        = "Error downloading file from S3"
  log_group_name = module.lamdba_flask_v2.lambda_log.name

  metric_transformation {
    name          = "DeputyReportingS3Error.${local.environment}"
    namespace     = "Integrations/Error"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "s3_error" {
  actions_enabled     = true
  alarm_name          = "deputy-reporting-${local.environment}-missing-from-s3"
  alarm_description   = "SERVICE: ${local.service}`\n`ENVIRONMENT: ${terraform.workspace}`\n`ERROR: File missing in S3"
  statistic           = "Sum"
  metric_name         = aws_cloudwatch_log_metric_filter.s3_error.metric_transformation[0].name
  comparison_operator = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm = 1
  evaluation_periods  = 1
  threshold           = local.threshold_alert_std
  period              = 60
  namespace           = aws_cloudwatch_log_metric_filter.s3_error.metric_transformation[0].namespace
  alarm_actions       = [data.aws_sns_topic.deputy_reporting_slack.arn]
  tags                = local.default_tags
}

resource "aws_cloudwatch_log_metric_filter" "api_gateway_report_errors" {
  name           = "deputy-reporting-gateway-report-errors.${local.environment}"
  pattern        = "{ ($.status = \"5*\") && ($.resourcePath = \"*/clients/*/reports\") }"
  log_group_name = "API-Gateway-Execution-Logs-deputy-reporting-${local.environment}-v2"

  metric_transformation {
    name          = "DeputyReportingReport500.${local.environment}"
    namespace     = "Integrations/Error"
    value         = "1"
    default_value = "0"
  }
  depends_on = [module.deploy_v2]
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_report_errors" {
  actions_enabled = true
  alarm_actions = [
    data.aws_sns_topic.rest_api.arn,
    data.aws_sns_topic.deputy_reporting_slack.arn
  ]
  alarm_name                = "deputy-reporting-${local.environment}-report-5xx-errors"
  alarm_description         = "SERVICE: ${local.service}`\n`ENVIRONMENT: ${terraform.workspace}`\n`ERROR: 5xx on Report Submission"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm       = 1
  evaluation_periods        = 1
  insufficient_data_actions = []
  metric_name               = "DeputyReportingReport500.${local.environment}"
  namespace                 = "Integrations/Error"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.threshold_alert_std
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_log_metric_filter" "api_gateway_supporting_errors" {
  name           = "deputy-reporting-gateway-supporting-errors.${local.environment}"
  pattern        = "{ ($.status = \"5*\") && ($.resourcePath = \"*/clients/*/reports/*/supportingdocuments*\") }"
  log_group_name = "API-Gateway-Execution-Logs-deputy-reporting-${local.environment}-v2"

  metric_transformation {
    name          = "DeputyReportingSupporting500.${local.environment}"
    namespace     = "Integrations/Error"
    value         = "1"
    default_value = "0"
  }
  depends_on = [module.deploy_v2]
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_supporting_errors" {
  actions_enabled = true
  alarm_actions = [
    data.aws_sns_topic.rest_api.arn,
    data.aws_sns_topic.deputy_reporting_slack.arn
  ]
  alarm_name                = "deputy-reporting-${local.environment}-supporting-5xx-errors"
  alarm_description         = "SERVICE: ${local.service}`\n`ENVIRONMENT: ${terraform.workspace}`\n`ERROR: 5xx on Supporting Doc Submission"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm       = 1
  evaluation_periods        = 1
  insufficient_data_actions = []
  metric_name               = "DeputyReportingSupporting500.${local.environment}"
  namespace                 = "Integrations/Error"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.threshold_alert_std
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_log_metric_filter" "api_gateway_checklist_errors" {
  name           = "deputy-reporting-gateway-checklist-errors.${local.environment}"
  pattern        = "{ ($.status = \"5*\") && ($.resourcePath = \"*/clients/*/reports/*/checklists*\") }"
  log_group_name = "API-Gateway-Execution-Logs-deputy-reporting-${local.environment}-v2"

  metric_transformation {
    name          = "DeputyReportingChecklist500.${local.environment}"
    namespace     = "Integrations/Error"
    value         = "1"
    default_value = "0"
  }
  depends_on = [module.deploy_v2]
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_checklist_errors" {
  actions_enabled = true
  alarm_actions = [
    data.aws_sns_topic.rest_api.arn,
    data.aws_sns_topic.deputy_reporting_slack.arn
  ]
  alarm_name                = "deputy-reporting-${local.environment}-checklist-5xx-errors"
  alarm_description         = "SERVICE: ${local.service}`\n`ENVIRONMENT: ${terraform.workspace}`\n`ERROR: 5xx on Checklist Submission"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm       = 1
  evaluation_periods        = 1
  insufficient_data_actions = []
  metric_name               = "DeputyReportingChecklist500.${local.environment}"
  namespace                 = "Integrations/Error"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.threshold_alert_std
  treat_missing_data        = "notBreaching"
}
