# Terraform — IaC по ТЗ

Минимальный набор: Kubernetes-кластер (EKS или AKS) и ресурсы для хранения данных (MySQL/RDS).

## Текущее состояние

В `main.tf` приведена **структура** и закомментированные примеры для:

- **AWS EKS** — кластер (нужно раскомментировать и добавить модуль `terraform-aws-modules/eks/aws`, VPC).
- **AWS RDS MySQL** — база данных для backend (нужно раскомментировать после настройки VPC).

Для полноценного запуска:

1. Установите провайдеры: `terraform init`
2. Создайте `terraform.tfvars` с нужными значениями (в т.ч. `db_password`).
3. Раскомментируйте в `main.tf` блоки `module "vpc"`, `module "eks"`, RDS и зависимые `output`.
4. Выполните `terraform plan` и `terraform apply`.

## Переменные

См. `variables.tf`. Обязательно задать `db_password` (через `tfvars` или `TF_VAR_db_password`).

## AKS (Azure)

Для Azure замените провайдер `aws` на `azurerm` и используйте модули/ресурсы AKS и Azure Database for MySQL по документации HashiCorp.
