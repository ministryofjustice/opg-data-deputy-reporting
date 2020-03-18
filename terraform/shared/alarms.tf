resource "aws_sns_topic" "api_gateway" {
  name = "api-gateway"
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_4xx_errors" {
  actions_enabled     = true
  alarm_actions       = [aws_sns_topic.api_gateway.arn]
  alarm_description   = "Number of 4XX Errors returned for Deputy Reporting API Gateway in ${terraform.workspace}"
  alarm_name          = "${local.environment}-api-gateway-4xx-errors"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = 2
  dimensions = {
    ApiName = "deputy-reporting-${terraform.workspace}"
  }
  evaluation_periods        = 5
  insufficient_data_actions = []
  metric_name               = "4XXError"
  namespace                 = "AWS/ApiGateway"
  ok_actions                = [aws_sns_topic.api_gateway.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.account.threshold
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_5xx_errors" {
  actions_enabled     = true
  alarm_actions       = [aws_sns_topic.api_gateway.arn]
  alarm_description   = "Number of 5XX Errors returned for Deputy Reporting API Gateway in ${terraform.workspace}"
  alarm_name          = "${local.environment}-api-gateway-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = 2
  dimensions = {
    ApiName = "deputy-reporting-${terraform.workspace}"
  }
  evaluation_periods        = 5
  insufficient_data_actions = []
  metric_name               = "5XXError"
  namespace                 = "AWS/ApiGateway"
  ok_actions                = [aws_sns_topic.api_gateway.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = local.account.threshold
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_high_count" {
  actions_enabled     = true
  alarm_actions       = [aws_sns_topic.api_gateway.arn]
  alarm_description   = "Number of requests for Deputy Reporting API Gateway in ${terraform.workspace}"
  alarm_name          = "${local.environment}-api-gateway-high-count"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = 1
  dimensions = {
    ApiName = "deputy-reporting-${terraform.workspace}"
  }
  evaluation_periods        = 1
  insufficient_data_actions = []
  metric_name               = "Count"
  namespace                 = "AWS/ApiGateway"
  ok_actions                = [aws_sns_topic.api_gateway.arn]
  period                    = 60
  statistic                 = "Sum"
  tags                      = {}
  threshold                 = 500
  treat_missing_data        = "notBreaching"
}

module "notify_slack" {
  source = "github.com/terraform-aws-modules/terraform-aws-notify-slack.git?ref=v2.10.0"

  sns_topic_name   = aws_sns_topic.api_gateway.name
  create_sns_topic = false

  lambda_function_name = "notify-slack"

  cloudwatch_log_group_retention_in_days = 14

  slack_webhook_url = data.aws_secretsmanager_secret_version.slack_webhook_url.secret_string
  slack_channel     = "#opg-integrations"
  slack_username    = "aws"
  slack_emoji       = ":warning:"

  tags = local.default_tags
}
