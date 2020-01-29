locals {
  lambda = "sirius-healthcheck-${local.environment}"
}

resource "aws_cloudwatch_log_group" "healthcheck_log_group" {
  name = "/aws/lambda/${local.lambda}"
}


resource "aws_lambda_function" "lambda_sirius_healthcheck" {
  filename         = data.archive_file.lambda_archive_sirius_healthcheck.output_path
  source_code_hash = data.archive_file.lambda_archive_sirius_healthcheck.output_base64sha256
  function_name    = local.lambda
  role             = aws_iam_role.lambda_sirius_healthcheck.arn
  handler          = "healthcheck.lambda_handler"
  runtime          = "python3.7"
  depends_on       = [aws_cloudwatch_log_group.healthcheck_log_group]
  vpc_config {
    subnet_ids         = tolist(data.aws_subnet_ids.private.ids)
    security_group_ids = [data.aws_security_group.lambda_api_ingress.id]
  }
  environment {
    variables = {
      BASE_URL = "http://api.${local.account["target_environment"]}.ecs"
    }
  }
}

data "archive_file" "lambda_archive_sirius_healthcheck" {
  type        = "zip"
  source_dir  = "../lambda"
  output_path = "./lambda.zip"
}
