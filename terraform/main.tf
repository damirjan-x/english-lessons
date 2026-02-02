# Infrastructure as Code — минимальный набор по ТЗ:
# Kubernetes-кластер (EKS или AKS) и ресурсы для хранения данных (MySQL/RDS или аналог).
#
# Вариант: AWS EKS + RDS MySQL (пример структуры).
# Для AKS замените провайдер и модули на azurerm.

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Опционально: remote backend (S3 + DynamoDB) для state
  # backend "s3" { bucket = "my-tf-state"; key = "english-lessons/terraform.tfstate"; region = "eu-central-1"; }
}

provider "aws" {
  region = var.aws_region
}

# Данные о доступных AZ
data "aws_availability_zones" "available" {
  state = "available"
}

# EKS cluster (минимальная конфигурация; для продакшена добавить node groups, private subnets)
# Раскомментируйте и настройте после установки модуля EKS (terraform-aws-modules/eks/aws).
#
# module "eks" {
#   source  = "terraform-aws-modules/eks/aws"
#   version = "~> 19.0"
#   cluster_name    = var.cluster_name
#   cluster_version = var.kubernetes_version
#   vpc_id          = module.vpc.vpc_id
#   subnet_ids      = module.vpc.private_subnets
#   enable_irsa     = true
#   cluster_endpoint_public_access = true
# }
#
# module "vpc" {
#   source  = "terraform-aws-modules/vpc/aws"
#   version = "~> 5.0"
#   name = "${var.project_name}-vpc"
#   cidr = var.vpc_cidr
#   azs  = slice(data.aws_availability_zones.available.names, 0, 3)
#   private_subnets = var.private_subnet_cidrs
#   public_subnets  = var.public_subnet_cidrs
#   enable_nat_gateway = true
#   single_nat_gateway = true
# }

# RDS MySQL — ресурс для хранения данных (по ТЗ)
# Раскомментируйте и настройте после добавления VPC/subnets.
#
# resource "aws_db_subnet_group" "main" {
#   name       = "${var.project_name}-db-subnet"
#   subnet_ids = module.vpc.database_subnets
# }
#
# resource "aws_security_group" "rds" {
#   name   = "${var.project_name}-rds"
#   vpc_id = module.vpc.vpc_id
#   ingress {
#     from_port   = 3306
#     to_port     = 3306
#     protocol    = "tcp"
#     cidr_blocks = [var.vpc_cidr]
#   }
# }
#
# resource "aws_db_instance" "mysql" {
#   identifier     = "${var.project_name}-mysql"
#   engine         = "mysql"
#   engine_version = "8.0"
#   instance_class = var.db_instance_class
#   allocated_storage = var.db_allocated_storage
#   db_name  = "english_lessons"
#   username = var.db_username
#   password = var.db_password
#   db_subnet_group_name   = aws_db_subnet_group.main.name
#   vpc_security_group_ids = [aws_security_group.rds.id]
#   publicly_accessible    = false
#   skip_final_snapshot    = true
# }

# Placeholder output (после раскомментирования модулей — вывести endpoint кластера и RDS)
output "aws_region" {
  value = var.aws_region
}

output "project_name" {
  value = var.project_name
}

# output "eks_cluster_endpoint" { value = module.eks.cluster_endpoint }
# output "rds_endpoint" { value = aws_db_instance.mysql.endpoint }
