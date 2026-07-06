resource "random_password" "db_password" {
  length  = 24
  special = false
}

resource "aws_security_group" "rds" {
  name        = "${local.name_prefix}-rds"
  description = "Allow PostgreSQL access from EKS nodes only"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
    description     = "EKS nodes"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_db_instance" "postgres" {
  identifier                     = "${local.name_prefix}-postgres"
  engine                         = "postgres"
  engine_version                 = var.db_engine_version
  instance_class                 = var.db_instance_class
  allocated_storage              = var.db_allocated_storage
  max_allocated_storage          = var.db_max_allocated_storage
  db_name                        = var.db_name
  username                       = var.db_username
  password                       = random_password.db_password.result
  db_subnet_group_name           = module.vpc.database_subnet_group_name
  vpc_security_group_ids         = [aws_security_group.rds.id]
  multi_az                       = false
  publicly_accessible            = false
  skip_final_snapshot            = true
  backup_retention_period        = 7
  deletion_protection            = false
  auto_minor_version_upgrade     = true
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  storage_encrypted              = true
  apply_immediately              = true

  tags = local.common_tags
}

