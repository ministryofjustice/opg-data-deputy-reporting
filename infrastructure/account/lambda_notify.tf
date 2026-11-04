# Notify Slack
resource "aws_lambda_function" "deputy_reporting_notify_slack" {
  function_name = "deputy-reporting-slack-notifier"
  role          = aws_iam_role.deputy_reporting_slack_lambda.arn
  handler       = "slack_notify.handler"
  runtime       = "python3.14"

  filename         = data.archive_file.slack_notify.output_path
  source_code_hash = data.archive_file.slack_notify.output_base64sha256

  tracing_config {
    mode = "Active"
  }
}

data "archive_file" "slack_notify" {
  type        = "zip"
  source_file = "${path.module}/../../lambda_functions/slack_notify/slack_notify.py"
  output_path = "${path.module}/../../lambda_functions/slack_notify/slack_notify.zip"
}

resource "aws_cloudwatch_log_group" "deputy_reporting_notify_slack" {
  name              = "/aws/lambda/${aws_lambda_function.deputy_reporting_notify_slack.function_name}"
  retention_in_days = 14
}


resource "aws_iam_role" "deputy_reporting_slack_lambda" {
  name               = "deputy-reporting-slack"
  assume_role_policy = data.aws_iam_policy_document.deputy_reporting_slack_lambda_assume.json
}


data "aws_iam_policy_document" "deputy_reporting_slack_lambda_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "deputy_reporting_notify_lambda" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
    ]
    resources = [
      aws_secretsmanager_secret.deputy_reporting_slack_webhook_url.arn,
    ]
  }

  statement {
    sid    = "AllowLambdaLogging"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
    ]
    resources = [
      aws_cloudwatch_log_group.deputy_reporting_notify_slack.arn,
      "${aws_cloudwatch_log_group.deputy_reporting_notify_slack.arn}:*",
    ]
  }

  statement {
    sid    = "SNS"
    effect = "Allow"
    actions = [
      "SNS:Subscribe",
      "SNS:Receive",
    ]
    resources = [
      aws_sns_topic.deputy_reporting.arn
    ]
  }

  statement {
    sid    = "SnsDecryptKms"
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources = [
      data.aws_kms_key.cloudwatch_sns.arn
    ]
  }
}

resource "aws_iam_policy" "deputy_reporting_notify_lambda" {
  name        = "deputy-reporting-slack-lambda"
  description = "Policy for the Slack Notify Lambda"
  policy      = data.aws_iam_policy_document.deputy_reporting_notify_lambda.json
}

resource "aws_iam_role_policy_attachment" "deputy_reporting_notify_lambda_attach" {
  role       = aws_iam_role.deputy_reporting_slack_lambda.name
  policy_arn = aws_iam_policy.deputy_reporting_notify_lambda.arn
}
