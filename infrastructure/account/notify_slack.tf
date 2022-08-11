data "aws_kms_key" "cloudwatch_sns" {
  key_id = "alias/integrations-sns-${terraform.workspace}"
}

resource "aws_sns_topic" "deputy_reporting" {
  name              = "deputy-reporting-slack-alerts"
  kms_master_key_id = data.aws_kms_key.cloudwatch_sns.key_id
}

module "notify_slack" {
  source = "github.com/terraform-aws-modules/terraform-aws-notify-slack.git?ref=v5.3.0"

  sns_topic_name   = aws_sns_topic.deputy_reporting.name
  create_sns_topic = false

  lambda_function_name = "notify-slack"

  cloudwatch_log_group_retention_in_days = 7

  slack_webhook_url = data.aws_secretsmanager_secret_version.slack_webhook_url.secret_string
  slack_channel     = terraform.workspace == "production" ? "#opg-digideps-devs" : "#opg-digideps-team"
  slack_username    = "aws"
  slack_emoji       = ":warning:"
}
