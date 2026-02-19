# Terraform — IaC для Oracle Cloud (OCI)

Создаёт в OCI:

- **VCN** (Virtual Cloud Network) с публичной и приватной подсетями
- **OKE** (Oracle Kubernetes Engine): кластер + node pool
- **MySQL Database Service** — управляемая БД для приложения

## Требования

- Аккаунт Oracle Cloud (OCI)
- API-ключ пользователя: в консоли OCI → Identity → Users → ваш пользователь → API Keys → Add API Key (скачать приватный ключ, сохранить fingerprint)
- Terraform >= 1.0

## Переменные (обязательные)

Задайте в `terraform.tfvars` или через переменные окружения `TF_VAR_*`:

| Переменная | Описание |
|------------|----------|
| `tenancy_ocid` | OCID тенанта (Profile → Tenancy → Copy OCID) |
| `user_ocid` | OCID пользователя (Identity → Users → Copy OCID) |
| `fingerprint` | Fingerprint API-ключа (Identity → Users → API Keys) |
| `private_key_path` | Путь к файлу `.pem` с приватным ключом (по умолчанию `~/.oci/oci_api_key.pem`) |
| `compartment_ocid` | OCID компартмента (Identity → Compartments → Copy OCID) |
| `db_password` | Пароль администратора MySQL: 8–32 символа, минимум 1 заглавная, 1 строчная, 1 цифра, 1 спецсимвол (не коммитить) |

Остальные переменные имеют значения по умолчанию (см. `variables.tf`).

## Запуск

```bash
cd terraform
terraform init
terraform plan   # проверить план
terraform apply  # создать ресурсы (подтвердить yes)
```

## После apply

1. **Kubeconfig для kubectl:** выполните команду из output `kubeconfig_command` (или вручную):
   ```bash
   oci ce cluster create-kubeconfig --cluster-id <cluster_id> --file $HOME/.kube/config --region <region> --token-version 2.0.0 --kube-endpoint PUBLIC_ENDPOINT
   ```
   Требуется установленный [OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm) и настроенный доступ к OCI.

2. **Подключение приложения к MySQL:** в Helm/ConfigMap укажите `MYSQL_HOST` = значение output `mysql_endpoint`, порт 3306. Имя БД по умолчанию создаётся при первом подключении или настройте в MySQL.

## Проверка работоспособности

После успешного `terraform apply`:

**1. Получить kubeconfig** (нужен установленный [OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm)):

```bash
oci ce cluster create-kubeconfig --cluster-id <cluster_id> --file %USERPROFILE%\.kube\config --region il-jerusalem-1 --token-version 2.0.0 --kube-endpoint PUBLIC_ENDPOINT
```

Подставьте свой `cluster_id` из output (или скопируйте команду из `kubeconfig_command`; на Windows замените `$HOME/.kube/config` на `%USERPROFILE%\.kube\config`).

**2. Проверить кластер:**

```bash
kubectl get nodes
kubectl get pods -A
```

Должны быть ноды в состоянии `Ready` и системные поды (например в `kube-system`) в `Running`.

**3. Задеплоить приложение (Helm)** — из корня проекта:

Создать Secret с паролем MySQL (используйте тот же пароль, что в `terraform.tfvars`):

```bash
kubectl create namespace english-lessons
kubectl create secret generic mysql-credentials --from-literal=mysql-password=ВАШ_MYSQL_ПАРОЛЬ -n english-lessons
```

Установить Helm-релиз с хостом MySQL из output (`mysql_endpoint`):

```bash
helm install english-lessons ./helm/english-lessons -n english-lessons --set mysql.host=10.0.2.133 --set mysql.user=admin --set mysql.existingSecret=mysql-credentials
```

Если ваш `mysql_endpoint` другой — подставьте его вместо `10.0.2.133`. Пользователь MySQL по умолчанию в Terraform — `admin`.

**4. Убедиться, что поды запустились:**

```bash
kubectl get pods -n english-lessons
kubectl logs -n english-lessons -l app.kubernetes.io/name=english-lessons -f
```

**5. Проверить API** (локально через port-forward):

```bash
kubectl port-forward -n english-lessons svc/english-lessons 8000:8000
```

Откройте в браузере: http://localhost:8000 (или http://localhost:8000/docs для Swagger). После проверки прервите port-forward (Ctrl+C).

Дальше можно настроить Ingress или LoadBalancer в `values.yaml` для доступа снаружи.

## Удаление

```bash
terraform destroy
```

## Форматы shape (примеры)

- **OKE node pool:** `VM.Standard.E4.Flex` (можно менять `node_pool_ocpus`, `node_pool_memory_gb`)
- **MySQL:** по умолчанию `MySQL.Free` (ECPU, бесплатный). При ошибке LimitExceeded задайте в `terraform.tfvars`: другой `mysql_shape_name` (например `MySQL.2` или `MySQL.VM.Standard.E4.1.8GB`) и/или `mysql_availability_domain_index = 1` или `2`.
