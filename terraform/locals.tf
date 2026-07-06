data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  azs         = slice(data.aws_availability_zones.available.names, 0, var.az_count)
  frontend_origin = var.frontend_domain_name != "" ? "https://${var.frontend_domain_name}" : "https://app.example.com"

  public_subnets = [
    for index, _ in local.azs : cidrsubnet(var.vpc_cidr, 8, index)
  ]

  private_subnets = [
    for index, _ in local.azs : cidrsubnet(var.vpc_cidr, 8, index + 10)
  ]

  database_subnets = [
    for index, _ in local.azs : cidrsubnet(var.vpc_cidr, 8, index + 20)
  ]

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.tags,
  )
}
