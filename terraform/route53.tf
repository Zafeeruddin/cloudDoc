data "aws_route53_zone" "selected" {
  count        = var.route53_zone_name != "" ? 1 : 0
  name         = var.route53_zone_name
  private_zone = false
}

resource "aws_route53_record" "frontend" {
  count   = var.route53_zone_name != "" && var.frontend_domain_name != "" && var.frontend_alb_dns_name != "" && var.frontend_alb_zone_id != "" ? 1 : 0
  zone_id = data.aws_route53_zone.selected[0].zone_id
  name    = var.frontend_domain_name
  type    = "A"

  alias {
    name                   = var.frontend_alb_dns_name
    zone_id                = var.frontend_alb_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "api" {
  count   = var.route53_zone_name != "" && length(aws_apigatewayv2_domain_name.api) > 0 ? 1 : 0
  zone_id = data.aws_route53_zone.selected[0].zone_id
  name    = aws_apigatewayv2_domain_name.api[0].domain_name
  type    = "A"

  alias {
    name                   = aws_apigatewayv2_domain_name.api[0].domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.api[0].domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

