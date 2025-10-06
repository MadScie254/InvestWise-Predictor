# KMS Key for encryption
resource "aws_kms_key" "main" {
  description             = "KMS key for InvestWise encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = local.tags
}

resource "aws_kms_alias" "main" {
  name          = "alias/${local.name}"
  target_key_id = aws_kms_key.main.key_id
}

# Random password for database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Secrets Manager for database credentials
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${local.name}-db-credentials"
  description             = "Database credentials for InvestWise"
  recovery_window_in_days = 7
  kms_key_id              = aws_kms_key.main.arn

  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = "investwise_user"
    password = random_password.db_password.result
  })
}

# Database subnet group
resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db-subnet-group"
  subnet_ids = module.vpc.database_subnets

  tags = merge(local.tags, {
    Name = "${local.name}-db-subnet-group"
  })
}

# Security group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "${local.name}-rds"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.cluster_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, {
    Name = "${local.name}-rds"
  })
}

# RDS PostgreSQL instance
resource "aws_db_instance" "main" {
  identifier = "${local.name}-postgres"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.main.arn

  db_name  = "investwise"
  username = "investwise_user"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = var.backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "Sun:04:00-Sun:05:00"

  deletion_protection = var.enable_deletion_protection
  skip_final_snapshot = !var.enable_deletion_protection

  # Enhanced monitoring
  monitoring_interval = var.enable_monitoring ? 60 : 0
  monitoring_role_arn = var.enable_monitoring ? aws_iam_role.rds_enhanced_monitoring[0].arn : null

  # Performance Insights
  performance_insights_enabled = var.enable_monitoring
  performance_insights_kms_key_id = var.enable_monitoring ? aws_kms_key.main.arn : null

  # Enable automatic minor version upgrade
  auto_minor_version_upgrade = true

  tags = merge(local.tags, {
    Name = "${local.name}-postgres"
  })
}

# IAM role for RDS enhanced monitoring
resource "aws_iam_role" "rds_enhanced_monitoring" {
  count = var.enable_monitoring ? 1 : 0
  name  = "${local.name}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  count      = var.enable_monitoring ? 1 : 0
  role       = aws_iam_role.rds_enhanced_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ElastiCache subnet group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${local.name}-cache-subnet"
  subnet_ids = module.vpc.private_subnets

  tags = local.tags
}

# Security group for ElastiCache
resource "aws_security_group" "elasticache" {
  name_prefix = "${local.name}-elasticache"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [module.eks.cluster_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, {
    Name = "${local.name}-elasticache"
  })
}

# ElastiCache Redis cluster
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${local.name}-redis"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = var.redis_num_cache_nodes
  parameter_group_name = "default.redis7"
  port                 = 6379
  
  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.elasticache.id]

  # Enable encryption
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = local.tags
}