locals {
  lambda = "${var.lambda_prefix}-${var.environment}"
}

resource "aws_cloudwatch_log_group" "healthcheck_log_group" {
  name = "/aws/lambda/${local.lambda}"
  tags = var.tags
}

resource "aws_lambda_function" "lambda_function" {
  filename         = data.archive_file.lambda_archive.output_path
  source_code_hash = data.archive_file.lambda_archive.output_base64sha256
  function_name    = local.lambda
  role             = aws_iam_role.lambda_role.arn
  handler          = var.handler
  runtime          = "python3.7"
  depends_on       = [aws_cloudwatch_log_group.healthcheck_log_group]
  layers           = [aws_lambda_layer_version.lambda_layer.arn]
  vpc_config {
    subnet_ids         = var.aws_subnet_ids
    security_group_ids = [data.aws_security_group.lambda_api_ingress.id]
  }
  environment {
    variables = {
      BASE_URL     = "http://api.${var.target_environment}.ecs"
      LOGGER_LEVEL = "${var.logger_level}"
    }
  }
  tracing_config {
    mode = "Active"
  }
  tags = var.tags
}

resource "aws_lambda_layer_version" "lambda_layer" {
  filename         = data.archive_file.lambda_layer_archive.output_path
  source_code_hash = data.archive_file.lambda_layer_archive.output_base64sha256
  layer_name       = "requirement_${var.target_environment}_${substr(replace(base64sha256(data.local_file.requirements.content_base64), "/[^0-9A-Za-z_]/", ""), 0, 5)}"

  compatible_runtimes = ["python3.7"]

  lifecycle {
    ignore_changes = [
      source_code_hash
    ]
  }
}

data "local_file" "requirements" {
  filename = "../../requirements/requirements.txt"
}

data "archive_file" "lambda_archive" {
  type        = "zip"
  source_dir  = "../../lambda_functions/${var.lambda_function_subdir}"
  output_path = "./lambda_${var.lambda_function_subdir}.zip"
}

data "archive_file" "lambda_layer_archive" {
  type        = "zip"
  source_dir  = "../../lambda_layers"
  output_path = "./lambda_layers_${var.lambda_function_subdir}.zip"
}