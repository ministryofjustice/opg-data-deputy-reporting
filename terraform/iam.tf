resource "aws_iam_role" "lambda_sirius_healthcheck" {
  name_prefix        = "lambda-${local.environment}-"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  lifecycle {
    create_before_destroy = true
  }
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "lambda" {
  name   = "lambda-${local.environment}"
  role   = aws_iam_role.lambda_sirius_healthcheck.id
  policy = data.aws_iam_policy_document.lambda_logging.json
}

data "aws_iam_policy_document" "lambda_logging" {
  statement {
    sid       = "allowLogging"
    effect    = "Allow"
    resources = [aws_cloudwatch_log_group.healthcheck_log_group.arn]
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]
  }
}

resource "aws_iam_role_policy_attachment" "vpc_access_execution_role" {
  role       = aws_iam_role.lambda_sirius_healthcheck.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}