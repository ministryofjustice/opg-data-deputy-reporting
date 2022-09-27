data "aws_sns_topic" "rest_api" {
  name = "rest-api"
}

data "aws_sns_topic" "deputy_reporting_slack" {
  name = "deputy-reporting-slack-alerts"
}

resource "aws_cloudwatch_metric_alarm" "rest_api_4xx_errors" {
  actions_enabled = true
  alarm_actions = [
    data.aws_sns_topic.rest_api.arn,
    data.aws_sns_topic.deputy_reporting_slack.arn
  ]
  alarm_name          = "deputy-reporting-${local.environment}-rest-api-4xx-errors"
  alarm_description   = "SERVICE: ${local.service}`\n`ENVIRONMENT: ${terraform.workspace}`\n`ERROR: 4xx"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm = 1
  dimensions = {
    ApiName = "deputy-reporting-${terraform.workspace}"
  }
  evaluation_periods        = 1
  insufficient_data_actions = []
  metric_name               = "4XXError"
  namespace                 = "AWS/ApiGateway"
  ok_actions                = [data.aws_sns_topic.rest_api.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.threshold_alert_4xx
  treat_missing_data        = "notBreaching"
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
  datapoints_to_alarm = 1
  dimensions = {
    ApiName = "deputy-reporting-${terraform.workspace}"
  }
  evaluation_periods        = 1
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
