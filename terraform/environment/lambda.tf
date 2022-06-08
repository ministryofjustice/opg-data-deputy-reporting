data "aws_ecr_repository" "deputy_reporting" {
  provider = aws.management
  name     = "integrations/deputy-reporting-lambda"
}

//Modify here for new version
module "lamdba_flask_v2" {
  source            = "./modules/lambda"
  lambda_name       = "deputy-reporting-${local.environment}-v2"
  description       = "Function to manage documents from digideps to sirius"
  working_directory = "/var/task"
  environment_variables = {
    SIRIUS_BASE_URL      = "http://api.${local.target_environment}.ecs"
    SIRIUS_API_VERSION   = "v1"
    ENVIRONMENT          = local.account.account_mapping
    LOGGER_LEVEL         = local.account.logger_level
    API_VERSION          = "v2"
    SESSION_DATA         = local.account.session_data
    DIGIDEPS_S3_BUCKET   = local.account.digideps_bucket_name
    DIGIDEPS_S3_ROLE_ARN = "arn:aws:iam::${local.account.digideps_account_id}:role/integrations-s3-read-${local.account.account_mapping}"
  }
  image_uri          = "${data.aws_ecr_repository.deputy_reporting.repository_url}:${var.image_tag}"
  ecr_arn            = data.aws_ecr_repository.deputy_reporting.arn
  tags               = local.default_tags
  account            = local.account
  environment        = local.environment
  rest_api           = aws_api_gateway_rest_api.deputy_reporting
  target_environment = local.target_environment
  aws_subnet_ids     = data.aws_subnet_ids.private.ids
  memory             = 1024
}