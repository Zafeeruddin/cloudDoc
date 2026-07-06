variable "project_name" {
  description = "Project name prefix for resource naming."
  type        = string
  default     = "docops"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "Primary VPC CIDR."
  type        = string
  default     = "10.20.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones to use."
  type        = number
  default     = 2
}

variable "cluster_version" {
  description = "EKS control plane version."
  type        = string
  default     = "1.30"
}

variable "node_instance_types" {
  description = "EKS managed node group instance types."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_desired_size" {
  description = "Desired worker node count."
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum worker node count."
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum worker node count."
  type        = number
  default     = 4
}

variable "db_name" {
  description = "RDS PostgreSQL database name."
  type        = string
  default     = "docops"
}

variable "db_username" {
  description = "RDS master username."
  type        = string
  default     = "docops"
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Initial RDS storage in GiB."
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum autoscaled RDS storage in GiB."
  type        = number
  default     = 100
}

variable "db_engine_version" {
  description = "PostgreSQL engine version."
  type        = string
  default     = "16.3"
}

variable "api_custom_domain_name" {
  description = "Optional custom domain for API Gateway."
  type        = string
  default     = ""
}

variable "frontend_domain_name" {
  description = "Optional Route53 record name for the frontend ALB."
  type        = string
  default     = ""
}

variable "route53_zone_name" {
  description = "Optional public hosted zone name used for frontend and API records."
  type        = string
  default     = ""
}

variable "acm_certificate_arn" {
  description = "Optional ACM certificate ARN for the API custom domain."
  type        = string
  default     = ""
}

variable "frontend_alb_dns_name" {
  description = "Optional frontend ALB DNS name created by the EKS ingress."
  type        = string
  default     = ""
}

variable "frontend_alb_zone_id" {
  description = "Optional hosted zone ID for the frontend ALB alias record."
  type        = string
  default     = ""
}

variable "backend_alb_listener_arn" {
  description = "Listener ARN of the internal backend ALB created by the Kubernetes ingress."
  type        = string
  default     = ""
}

variable "backend_alb_security_group_id" {
  description = "Optional backend ALB security group ID to allow API Gateway VPC link traffic."
  type        = string
  default     = ""
}

variable "allowed_bearer_prefix" {
  description = "Mock authorizer bearer token prefix."
  type        = string
  default     = "docops:"
}

variable "tags" {
  description = "Additional tags applied to all supported resources."
  type        = map(string)
  default     = {}
}

