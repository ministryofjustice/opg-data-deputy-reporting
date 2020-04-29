resource "aws_sns_topic" "rest_api" {
  name = "rest-api"
}

module "notify_slack" {
  source = "github.com/terraform-aws-modules/terraform-aws-notify-slack.git?ref=v2.10.0"

  sns_topic_name   = aws_sns_topic.rest_api.name
  create_sns_topic = false

  lambda_function_name = "notify-slack"

  cloudwatch_log_group_retention_in_days = 14

  slack_webhook_url = data.aws_secretsmanager_secret_version.slack_webhook_url.secret_string
  slack_channel     = local.account.alerts_channel
  slack_username    = "aws"
  slack_emoji       = ":warning:"

  tags = local.default_tags
}
