resource "aws_security_group" "vpc_link" {
  name        = "${local.name_prefix}-apigw-vpc-link"
  description = "Security group for API Gateway VPC Link to the internal backend ALB"
  vpc_id      = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  tags = local.common_tags
}

resource "aws_security_group_rule" "allow_vpc_link_to_backend_alb" {
  count                    = var.backend_alb_security_group_id != "" ? 1 : 0
  type                     = "ingress"
  from_port                = 80
  to_port                  = 80
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.vpc_link.id
  security_group_id        = var.backend_alb_security_group_id
  description              = "Allow API Gateway VPC Link to reach the internal backend ALB"
}

resource "aws_apigatewayv2_vpc_link" "backend" {
  name               = "${local.name_prefix}-backend"
  subnet_ids         = module.vpc.private_subnets
  security_group_ids = [aws_security_group.vpc_link.id]
  tags               = local.common_tags
}

resource "aws_apigatewayv2_api" "http" {
  name          = "${local.name_prefix}-http"
  protocol_type = "HTTP"

  cors_configuration {
    allow_headers = ["authorization", "content-type", "x-user-id", "x-user-email", "x-user-name"]
    allow_methods = ["GET", "POST", "DELETE", "OPTIONS"]
    allow_origins = [local.frontend_origin]
  }

  tags = local.common_tags
}

resource "aws_lambda_permission" "authorizer" {
  statement_id  = "AllowHttpApiAuthorizerInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.authorizer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/authorizers/*"
}

resource "aws_apigatewayv2_authorizer" "lambda" {
  api_id                            = aws_apigatewayv2_api.http.id
  authorizer_type                   = "REQUEST"
  authorizer_uri                    = aws_lambda_function.authorizer.invoke_arn
  identity_sources                  = ["$request.header.Authorization"]
  name                              = "${local.name_prefix}-authorizer"
  authorizer_payload_format_version = "2.0"
  enable_simple_responses           = true
}

resource "aws_apigatewayv2_integration" "backend" {
  count = var.backend_alb_listener_arn != "" ? 1 : 0

  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "HTTP_PROXY"
  integration_method     = "ANY"
  integration_uri        = var.backend_alb_listener_arn
  payload_format_version = "1.0"
  connection_type        = "VPC_LINK"
  connection_id          = aws_apigatewayv2_vpc_link.backend.id
  timeout_milliseconds   = 30000

  request_parameters = {
    "overwrite:header.x-user-id"    = "$context.authorizer.userId"
    "overwrite:header.x-user-email" = "$context.authorizer.userEmail"
    "overwrite:header.x-user-name"  = "$context.authorizer.userName"
  }
}

resource "aws_apigatewayv2_route" "proxy" {
  count = var.backend_alb_listener_arn != "" ? 1 : 0

  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "ANY /{proxy+}"
  authorization_type = "CUSTOM"
  authorizer_id      = aws_apigatewayv2_authorizer.lambda.id
  target             = "integrations/${aws_apigatewayv2_integration.backend[0].id}"
}

resource "aws_apigatewayv2_route" "root" {
  count = var.backend_alb_listener_arn != "" ? 1 : 0

  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "ANY /"
  authorization_type = "CUSTOM"
  authorizer_id      = aws_apigatewayv2_authorizer.lambda.id
  target             = "integrations/${aws_apigatewayv2_integration.backend[0].id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apigw_access.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      sourceIp       = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      responseLength = "$context.responseLength"
    })
  }

  default_route_settings {
    detailed_metrics_enabled = true
    throttling_burst_limit   = 200
    throttling_rate_limit    = 100
  }

  tags = local.common_tags
}

resource "aws_apigatewayv2_domain_name" "api" {
  count = var.api_custom_domain_name != "" && var.acm_certificate_arn != "" ? 1 : 0

  domain_name = var.api_custom_domain_name
  domain_name_configuration {
    certificate_arn = var.acm_certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  tags = local.common_tags
}

resource "aws_apigatewayv2_api_mapping" "api" {
  count = length(aws_apigatewayv2_domain_name.api) > 0 ? 1 : 0

  api_id      = aws_apigatewayv2_api.http.id
  domain_name = aws_apigatewayv2_domain_name.api[0].id
  stage       = aws_apigatewayv2_stage.default.id
}
