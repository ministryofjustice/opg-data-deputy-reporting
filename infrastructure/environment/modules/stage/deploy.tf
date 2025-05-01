locals {
  lambda_version_folder_sha = substr(replace(base64sha256(data.local_file.lambda_version_folder_sha.content_base64), "/[^0-9A-Za-z_]/", ""), 0, 5)
}

data "local_file" "openapispec" {
  filename = "../../lambda_functions/${var.openapi_version}/openapi/${var.api_name}-openapi.yml"
}

data "local_file" "lambda_version_folder_sha" {
  filename = "../../lambda_functions/${var.openapi_version}/directory_sha"
}

resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = var.rest_api.id
  depends_on  = [var.domain_name]
  triggers = {
    // Force a deploy on when content has changed
    open_api_spec             = var.content_api_sha
    api_gateway_policy        = var.content_api_gateway_policy_sha
    lambda_version_folder_sha = local.lambda_version_folder_sha
  }
  lifecycle {
    create_before_destroy = true
  }
}
