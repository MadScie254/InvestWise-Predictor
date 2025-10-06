# Data sources
data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

data "aws_caller_identity" "current" {}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = local.name
  cidr = "10.0.0.0/16"

  azs             = local.azs
  private_subnets = [for k, v in local.azs : cidrsubnet("10.0.0.0/16", 4, k)]
  public_subnets  = [for k, v in local.azs : cidrsubnet("10.0.0.0/16", 8, k + 48)]
  database_subnets = [for k, v in local.azs : cidrsubnet("10.0.0.0/16", 8, k + 52)]

  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true

  # Database subnet group
  create_database_subnet_group = true
  create_database_subnet_route_table = true

  # VPC Flow Logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_iam_role  = true
  create_flow_log_cloudwatch_log_group = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }

  tags = local.tags
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = local.name
  cluster_version = var.cluster_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  # EKS Managed Node Group(s)
  eks_managed_node_group_defaults = {
    instance_types = var.node_group_instance_types
    
    # We are using the IRSA created below for permissions
    # However, we have to deploy with the policy attached FIRST (when creating a fresh cluster)
    # and then turn this off after the cluster/node group is created. Without this initial policy,
    # the VPC CNI fails to assign IPs and nodes cannot join the cluster
    iam_role_attach_cni_policy = true
  }

  eks_managed_node_groups = {
    main = {
      name = "main-node-group"

      instance_types = var.node_group_instance_types
      capacity_type  = "ON_DEMAND"

      min_size     = var.node_group_min_size
      max_size     = var.node_group_max_size
      desired_size = var.node_group_desired_size

      # Launch template configuration
      create_launch_template = false
      launch_template_name   = ""

      disk_size = 50

      # Remote access via EC2 Instance Connect
      remote_access = {
        ec2_ssh_key               = aws_key_pair.main.key_name
        source_security_group_ids = [aws_security_group.node_group_one.id]
      }

      # Labels
      labels = {
        Environment = var.environment
        NodeGroup   = "main"
      }

      # Taints
      taints = []

      update_config = {
        max_unavailable_percentage = 25
      }

      tags = local.tags
    }
  }

  # Cluster access entry
  # To add the current caller identity as an administrator
  enable_cluster_creator_admin_permissions = true

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  tags = local.tags
}

# Key pair for EC2 instances
resource "aws_key_pair" "main" {
  key_name   = "${local.name}-key"
  public_key = file("${path.module}/key.pub")  # You need to create this file

  tags = local.tags
}

# Security group for additional access to the node groups
resource "aws_security_group" "node_group_one" {
  name_prefix = "${local.name}-node-group-one"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"

    cidr_blocks = [
      "10.0.0.0/8",
    ]
  }

  tags = local.tags
}