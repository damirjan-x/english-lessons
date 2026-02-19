# OCI: VCN + OKE (публичная подсеть) + MySQL (приватная, без выхода в интернет)
# Без NAT Gateway — ноды в публичной подсети, трафик через Internet Gateway

terraform {
  required_version = ">= 1.0"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 8.0"
    }
  }
}

provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_ocid
}

# Доступные версии Kubernetes в регионе (для il-jerusalem-1 и др. — список может отличаться)
data "oci_containerengine_cluster_option" "oke" {
  cluster_option_id = "all"
  compartment_id   = var.compartment_ocid
}

# Версия K8s: из переменной или первая доступная в регионе (API возвращает значения с префиксом "v")
locals {
  available_versions = data.oci_containerengine_cluster_option.oke.kubernetes_versions
  kubernetes_version = var.kubernetes_version != "" ? var.kubernetes_version : (
    length(local.available_versions) > 0 ? local.available_versions[0] : "v1.32.1"
  )
}

# VCN
resource "oci_core_vcn" "main" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = [var.vcn_cidr]
  display_name   = "${var.project_name}-vcn"
  dns_label      = substr(var.project_name, 0, 15)
}

resource "oci_core_internet_gateway" "ig" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-ig"
}

# Публичная подсеть: 0.0.0.0/0 -> IGW (только OKE endpoint и service LB; ноды — в отдельной подсети)
resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-rt-public"
  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.ig.id
  }
}

# Приватная подсеть: без маршрута в интернет (только MySQL)
resource "oci_core_route_table" "private" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-rt-private"
}

# Security list — публичная подсеть (Kubernetes API endpoint + LB)
# По документации OKE: API endpoint должен принимать от worker nodes TCP 6443 и 12250
resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-sl-public"
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
  # Worker nodes → Kubernetes API (обязательно для регистрации нод)
  ingress_security_rules {
    protocol = "6"
    source   = var.nodes_subnet_cidr
    tcp_options {
      min = 6443
      max = 6443
    }
  }
  ingress_security_rules {
    protocol = "6"
    source   = var.nodes_subnet_cidr
    tcp_options {
      min = 12250
      max = 12250
    }
  }
  ingress_security_rules {
    protocol = "1"
    source   = var.nodes_subnet_cidr
    icmp_options { type = 3 }
  }
  ingress_security_rules {
    protocol = "1"
    source   = var.nodes_subnet_cidr
    icmp_options { type = 4 }
  }
  # Доступ к API и LB из VCN и из интернета
  ingress_security_rules {
    protocol = "6"
    source   = var.vcn_cidr
    tcp_options {
      min = 443
      max = 443
    }
  }
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }
  # kubectl с вашего ПК: доступ к Kubernetes API по 6443 из интернета
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 6443
      max = 6443
    }
  }
}

# Security list — подсеть нод (node pool; трафик в интернет через IGW)
resource "oci_core_security_list" "nodes" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-sl-nodes"
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
  ingress_security_rules {
    protocol = "all"
    source   = var.vcn_cidr
  }
}

# Security list — приватная подсеть (MySQL)
resource "oci_core_security_list" "private" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-sl-private"
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
  ingress_security_rules {
    protocol = "all"
    source   = var.vcn_cidr
  }
  ingress_security_rules {
    protocol = "6"
    source   = var.vcn_cidr
    tcp_options { 
      min = 3306
      max = 3306 
      }
  }
}

resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.main.id
  cidr_block                 = var.public_subnet_cidr
  display_name               = "${var.project_name}-subnet-public"
  dns_label                  = "public"
  route_table_id             = oci_core_route_table.public.id
  security_list_ids          = [oci_core_security_list.public.id]
  prohibit_public_ip_on_vnic  = false
}

# Подсеть для node pool (отдельно от public: service subnets не могут использоваться нодами)
resource "oci_core_subnet" "nodes" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.main.id
  cidr_block                 = var.nodes_subnet_cidr
  display_name               = "${var.project_name}-subnet-nodes"
  dns_label                  = "nodes"
  route_table_id             = oci_core_route_table.public.id
  security_list_ids          = [oci_core_security_list.nodes.id]
  prohibit_public_ip_on_vnic  = false
}

resource "oci_core_subnet" "private" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.main.id
  cidr_block                 = var.private_subnet_cidr
  display_name               = "${var.project_name}-subnet-private"
  dns_label                  = "private"
  route_table_id             = oci_core_route_table.private.id
  security_list_ids          = [oci_core_security_list.private.id]
  prohibit_public_ip_on_vnic = true
}

# OKE
resource "oci_containerengine_cluster" "oke" {
  compartment_id     = var.compartment_ocid
  kubernetes_version = local.kubernetes_version
  name               = var.cluster_name
  vcn_id             = oci_core_vcn.main.id
  endpoint_config {
    is_public_ip_enabled = true
    subnet_id            = oci_core_subnet.public.id
  }
  options {
    service_lb_subnet_ids = [oci_core_subnet.public.id]
  }
  lifecycle {
    ignore_changes = [kubernetes_version]
  }
}

data "oci_core_images" "node_images" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Oracle Linux"
  operating_system_version = "8"
  shape                    = var.node_pool_shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

# Node pool в публичной подсети — образы и обновления через IGW, без NAT
# Для региональной подсети (il-jerusalem-1 и др.) нужен node_config_details с placement_configs по AD
resource "oci_containerengine_node_pool" "pool" {
  cluster_id         = oci_containerengine_cluster.oke.id
  compartment_id     = var.compartment_ocid
  kubernetes_version = local.kubernetes_version
  name               = "${var.cluster_name}-pool1"
  node_shape         = var.node_pool_shape

  node_config_details {
    dynamic "placement_configs" {
      for_each = data.oci_identity_availability_domains.ads.availability_domains
      content {
        availability_domain = placement_configs.value.name
        subnet_id          = oci_core_subnet.nodes.id
      }
    }
    size = var.node_pool_size
  }

  node_shape_config {
    ocpus         = var.node_pool_ocpus
    memory_in_gbs = var.node_pool_memory_gb
  }
  node_source_details {
    image_id    = data.oci_core_images.node_images.images[0].id
    source_type = "IMAGE"
  }
  initial_node_labels {
    key   = "name"
    value = var.cluster_name
  }
  lifecycle {
    ignore_changes = [kubernetes_version]
  }
}

# MySQL в приватной подсети (без выхода в интернет)
resource "oci_mysql_mysql_db_system" "mysql" {
  admin_password          = var.db_password
  admin_username          = var.db_username
  availability_domain     = data.oci_identity_availability_domains.ads.availability_domains[var.mysql_availability_domain_index].name
  compartment_id          = var.compartment_ocid
  shape_name              = var.mysql_shape_name
  subnet_id               = oci_core_subnet.private.id
  display_name            = "${var.project_name}-mysql"
  hostname_label          = "mysql"
  data_storage_size_in_gb = var.mysql_data_storage_gb
  is_highly_available      = false
}

# Outputs
output "cluster_id"            { value = oci_containerengine_cluster.oke.id }
output "cluster_name"          { value = oci_containerengine_cluster.oke.name }
output "kubernetes_version" {
  value       = local.kubernetes_version
  description = "Версия K8s, выбранная для кластера и node pool"
}
output "mysql_endpoint"      { value = oci_mysql_mysql_db_system.mysql.ip_address }
output "region"              { value = var.region }
output "vcn_id"              { value = oci_core_vcn.main.id }
output "kubeconfig_command"  {
  value = "oci ce cluster create-kubeconfig --cluster-id ${oci_containerengine_cluster.oke.id} --file $HOME/.kube/config --region ${var.region} --token-version 2.0.0 --kube-endpoint PUBLIC_ENDPOINT"
}
