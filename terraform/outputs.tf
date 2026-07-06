output "vpc_id" {
  value = module.vpc.vpc_id
}

output "public_subnet_ids" {
  value = module.vpc.public_subnets
}

output "app_private_subnet_ids" {
  value = module.vpc.private_subnets
}

output "db_private_subnet_ids" {
  value = module.vpc.database_subnets
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_oidc_provider_arn" {
  value = module.eks.oidc_provider_arn
}

output "backend_irsa_role_arn" {
  value = aws_iam_role.backend_irsa.arn
}

output "worker_irsa_role_arn" {
  value = aws_iam_role.worker_irsa.arn
}

output "documents_bucket_name" {
  value = aws_s3_bucket.documents.bucket
}

output "processing_queue_url" {
  value = aws_sqs_queue.processing.url
}

output "processing_queue_arn" {
  value = aws_sqs_queue.processing.arn
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "rds_database_url" {
  sensitive = true
  value     = "postgresql+psycopg://${var.db_username}:${random_password.db_password.result}@${aws_db_instance.postgres.address}:5432/${var.db_name}"
}

output "http_api_id" {
  value = aws_apigatewayv2_api.http.id
}

output "http_api_default_invoke_url" {
  value = aws_apigatewayv2_stage.default.invoke_url
}

output "vpc_link_security_group_id" {
  value = aws_security_group.vpc_link.id
}

output "authorizer_function_name" {
  value = aws_lambda_function.authorizer.function_name
}

