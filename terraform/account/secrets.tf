resource "aws_secretsmanager_secret" "slack_webhook_url" {
  name = "slack_webhook_url"
}

data "aws_secretsmanager_secret_version" "slack_webhook_url" {
  secret_id = aws_secretsmanager_secret.slack_webhook_url.id
}
