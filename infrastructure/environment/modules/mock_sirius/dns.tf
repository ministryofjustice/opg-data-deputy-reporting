resource "aws_service_discovery_private_dns_namespace" "deputy_reporting" {
  name = "deputy-reporting-${var.environment}.ecs"
  vpc  = var.vpc_id
  tags = var.tags
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

  tags          = var.tags
  force_destroy = true
}
