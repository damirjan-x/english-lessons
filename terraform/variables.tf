# OCI — идентификаторы и доступ
variable "tenancy_ocid" {
  description = "OCID тенанта OCI"
  type        = string
}

variable "user_ocid" {
  description = "OCID пользователя IAM (API key принадлежит этому пользователю)"
  type        = string
}

variable "fingerprint" {
  description = "Fingerprint публичного API-ключа пользователя"
  type        = string
}

variable "private_key_path" {
  description = "Путь к файлу приватного API-ключа (PEM)"
  type        = string
  default     = "~/.oci/oci_api_key.pem"
}

variable "region" {
  description = "Регион OCI (например eu-frankfurt-1, us-ashburn-1)"
  type        = string
  default     = "eu-frankfurt-1"
}

variable "compartment_ocid" {
  description = "OCID компартмента, в котором создаются ресурсы"
  type        = string
}

# Имена и параметры проекта
variable "project_name" {
  description = "Префикс имён ресурсов"
  type        = string
  default     = "englishlessons"
}

variable "cluster_name" {
  description = "Имя кластера OKE"
  type        = string
  default     = "englishlessons-oke"
}

variable "kubernetes_version" {
  description = "Версия Kubernetes для OKE (с префиксом v, например v1.32.1). Пустая строка = авто (первая доступная в регионе из API)"
  type        = string
  default     = ""
}

# Сеть (VCN)
variable "vcn_cidr" {
  description = "CIDR блок VCN"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR публичной подсети (OKE endpoint, LB)"
  type        = string
  default     = "10.0.1.0/24"
}

variable "nodes_subnet_cidr" {
  description = "CIDR подсети для OKE node pool (должна быть отдельно от service_lb_subnet_ids)"
  type        = string
  default     = "10.0.3.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR приватной подсети (MySQL)"
  type        = string
  default     = "10.0.2.0/24"
}

# OKE Node Pool
variable "node_pool_shape" {
  description = "Shape нод OKE (например VM.Standard.E4.Flex)"
  type        = string
  default     = "VM.Standard.E4.Flex"
}

variable "node_pool_ocpus" {
  description = "Количество OCPU на ноду"
  type        = number
  default     = 1
}

variable "node_pool_memory_gb" {
  description = "Память (GB) на ноду"
  type        = number
  default     = 16
}

variable "node_pool_size" {
  description = "Количество нод в пуле (на подсеть)"
  type        = number
  default     = 1
}

# MySQL Database Service
variable "mysql_shape_name" {
  description = "Shape MySQL. По умолчанию MySQL.Free (ECPU, бесплатный). Варианты: MySQL.Free, MySQL.2, MySQL.4; или OCPU MySQL.VM.Standard.E4.1.8GB. MySQL.HeatWave.VM.Standard.E3 для новых пользователей недоступен (лимит 0)."
  type        = string
  default     = "MySQL.Free"
}

variable "mysql_availability_domain_index" {
  description = "Индекс Availability Domain для MySQL (0, 1 или 2). Меняйте, если в текущем AD исчерпан лимит по выбранному shape."
  type        = number
  default     = 0
}

variable "mysql_data_storage_gb" {
  description = "Размер хранилища MySQL (GB)"
  type        = number
  default     = 50
}

variable "db_username" {
  description = "Имя администратора MySQL"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "db_password" {
  description = "Пароль администратора MySQL. OCI требует: 8–32 символа, минимум 1 заглавная, 1 строчная, 1 цифра, 1 спецсимвол"
  type        = string
  sensitive   = true
}
