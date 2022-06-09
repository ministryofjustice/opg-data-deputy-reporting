data "aws_ecr_repository" "mock_sirius" {
  provider = aws.management
  name     = "integrations/deputy-reporting-mock-sirius"
}

resource "aws_ecs_task_definition" "deputy_reporting_mock_sirius" {
  family                   = "deputy-reporting-mock-sirius-${terraform.workspace}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  container_definitions    = "[${local.deputy_reporting_mock_sirius}]"
  task_role_arn            = aws_iam_role.data_deputy_reporting.arn
  execution_role_arn       = aws_iam_role.execution_role.arn
  tags = merge(local.default_tags,
    { "Role" = "deputy-reporting-mock-sirius-${local.environment}" },
  )
}

resource "aws_service_discovery_private_dns_namespace" "deputy_reporting" {
  name = "deputy-reporting-${local.environment}.ecs"
  vpc  = local.account.vpc_id
  tags = local.default_tags
}

resource "aws_service_discovery_service" "deputy_reporting_mock_sirius" {
  name = "deputy-reporting-mock-sirius"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.deputy_reporting.id
    dns_records {
      ttl  = 10
      type = "A"
    }
    routing_policy = "MULTIVALUE"
  }

  tags          = local.default_tags
  force_destroy = true
}

resource "aws_ecs_service" "mock_sirius" {
  name                    = aws_ecs_task_definition.deputy_reporting_mock_sirius.family
  cluster                 = aws_ecs_cluster.deputy_reporting.id
  task_definition         = aws_ecs_task_definition.deputy_reporting_mock_sirius.arn
  desired_count           = 1
  launch_type             = "FARGATE"
  platform_version        = "1.4.0"
  enable_ecs_managed_tags = true
  propagate_tags          = "SERVICE"
  wait_for_steady_state   = true
  tags                    = local.default_tags

  network_configuration {
    security_groups  = [aws_security_group.deputy_reporting_mock_sirius.id]
    subnets          = data.aws_subnet_ids.private.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.deputy_reporting_mock_sirius.arn
  }
}

locals {
  deputy_reporting_mock_sirius = jsonencode({
    cpu       = 0,
    essential = true,
    image     = "${data.aws_ecr_repository.mock_sirius.repository_url}:${var.image_tag}",
    name      = "mock-sirius",
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = aws_cloudwatch_log_group.deputy_reporting.name,
        awslogs-region        = "eu-west-1",
        awslogs-stream-prefix = "deputy-reporting-mock-sirius-${local.environment}"
      }
    },
  })
}

resource "aws_ecs_cluster" "deputy_reporting" {
  name = "deputy-reporting-${local.environment}"
  tags = local.default_tags
}

resource "aws_cloudwatch_log_group" "deputy_reporting" {
  name              = "deputy-reporting-${local.environment}"
  retention_in_days = 3
  tags              = local.default_tags
}

//EXECUTION ROLES

resource "aws_iam_role" "execution_role" {
  name               = "deputy-reporting-execution-role.${local.environment}"
  assume_role_policy = data.aws_iam_policy_document.execution_role_assume_policy.json
  tags               = local.default_tags
}

data "aws_iam_policy_document" "execution_role_assume_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["ecs-tasks.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_iam_role_policy" "execution_role" {
  policy = data.aws_iam_policy_document.execution_role.json
  role   = aws_iam_role.execution_role.id
}

data "aws_iam_policy_document" "execution_role" {
  statement {
    effect    = "Allow"
    resources = ["*"]

    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
  }
}

//TASK ROLE

resource "aws_iam_role" "deputy_reporting_mock_sirius" {
  assume_role_policy = data.aws_iam_policy_document.task_role_assume_policy.json
  name               = "deputy-reporting-mock-sirius-${local.environment}"
  tags               = local.default_tags
}

data "aws_iam_policy_document" "task_role_assume_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["ecs-tasks.amazonaws.com"]
      type        = "Service"
    }
  }
}

// SECURITY GROUP
resource "aws_security_group" "deputy_reporting_mock_sirius" {
  name_prefix = "deputy-reporting-mock-sirius-${terraform.workspace}-"
  vpc_id      = local.account.vpc_id
  description = "Mock Sirius Deputy Reporting ECS task"

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    local.default_tags,
    tomap({ "Name" : "deputy-reporting-mock-sirius-${terraform.workspace}" })
  )
}

data "aws_security_group" "lambda_api_ingress" {
  filter {
    name   = "tag:Name"
    values = ["integration-lambda-api-access-${local.target_environment}"]
  }
}

//RULES FOR APP ACCESS
resource "aws_security_group_rule" "lambda_to_mock_sirius" {
  type                     = "ingress"
  from_port                = 80
  to_port                  = 80
  protocol                 = "tcp"
  source_security_group_id = data.aws_security_group.lambda_api_ingress.id
  security_group_id        = aws_security_group.deputy_reporting_mock_sirius.id
  description              = "Deputy Reporting Lambda to Mock Sirius"
}
