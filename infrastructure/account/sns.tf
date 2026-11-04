# Slack Alerts SNS Topic
data "aws_kms_key" "cloudwatch_sns" {
  key_id = "alias/integrations-sns-${terraform.workspace}"
}

resource "aws_sns_topic" "deputy_reporting" {
  name              = "deputy-reporting-slack-alerts"
  kms_master_key_id = data.aws_kms_key.cloudwatch_sns.key_id
}

resource "aws_sns_topic_policy" "deputy_reporting_slack_notifications" {
  arn    = aws_sns_topic.deputy_reporting.arn
  policy = data.aws_iam_policy_document.deputy_reporting_slack_notifications.json
}

data "aws_iam_policy_document" "deputy_reporting_slack_notifications" {
  statement {
    sid    = "Publish SNS"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }

    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.deputy_reporting.arn]
  }
}

resource "aws_sns_topic_subscription" "deputy_reporting_slack_notifications_lambda" {
  topic_arn = aws_sns_topic.deputy_reporting.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.deputy_reporting_notify_slack.arn
}

resource "aws_lambda_permission" "deputy_reporting_slack_notifications_allow" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.deputy_reporting_notify_slack.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.deputy_reporting.arn
  lifecycle {
    replace_triggered_by = [
      aws_lambda_function.deputy_reporting_notify_slack
    ]
  }
}
