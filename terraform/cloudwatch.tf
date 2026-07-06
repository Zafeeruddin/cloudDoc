resource "aws_cloudwatch_log_group" "apigw_access" {
  name              = "/aws/apigateway/${local.name_prefix}"
  retention_in_days = 30
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "authorizer" {
  name              = "/aws/lambda/${local.name_prefix}-authorizer"
  retention_in_days = 30
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "application" {
  name              = "/docops/${local.name_prefix}/application"
  retention_in_days = 30
  tags              = local.common_tags
}

