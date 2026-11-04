
module "notify_slack" {
  source = "github.com/terraform-aws-modules/terraform-aws-notify-slack.git?ref=v7.5.2"

  sns_topic_name   = aws_sns_topic.deputy_reporting.name
  create_sns_topic = false

  lambda_function_name = "notify-slack"

  cloudwatch_log_group_retention_in_days = 7

  slack_webhook_url = data.aws_secretsmanager_secret_version.slack_webhook_url.secret_string
  slack_channel     = terraform.workspace == "production" ? "#opg-digideps-team" : "#integrations-alerts"
  slack_username    = "aws"
  slack_emoji       = ":warning:"
}
