locals {
  lambda = "${var.lambda_prefix}-${var.environment}"
}

resource "aws_cloudwatch_log_group" "healthcheck_log_group" {
  name = "/aws/lambda/${local.lambda}"
}

resource "aws_lambda_function" "lambda_function" {
  filename         = data.archive_file.lambda_archive.output_path
  source_code_hash = data.archive_file.lambda_archive.output_base64sha256
  function_name    = local.lambda
  role             = aws_iam_role.lambda_role.arn
  handler          = var.handler
  runtime          = "python3.7"
  depends_on       = [aws_cloudwatch_log_group.healthcheck_log_group]
  vpc_config {
    subnet_ids         = var.aws_subnet_ids
    security_group_ids = [data.aws_security_group.lambda_api_ingress.id]
  }
  environment {
    variables = {
      BASE_URL = "http://api.${var.target_environment}.ecs"
    }
  }
}

data "archive_file" "lambda_archive" {
  type        = "zip"
  source_dir  = "../lambda_functions/${var.lambda_function_subdir}"
  output_path = "./lambda_${var.lambda_function_subdir}.zip"
}
