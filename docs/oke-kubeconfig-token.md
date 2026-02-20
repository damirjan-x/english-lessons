# Kubeconfig с токеном для OKE (CI/CD без exec)

Чтобы GitHub Actions подключался к OKE без OCI CLI, нужен kubeconfig, где пользователь задан **токеном** сервисного аккаунта, а не блоком `exec`.

## Шаг 1: Подключиться к кластеру (текущий kubeconfig с OCI)

Убедитесь, что с вашей машины работает `kubectl` (kubeconfig с exec/oci). Например:

```powershell
kubectl get nodes
```

## Шаг 2: Создать сервисный аккаунт и привязку роли

```powershell
kubectl -n kube-system create serviceaccount kubeconfig-sa
kubectl create clusterrolebinding add-on-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:kubeconfig-sa
```

## Шаг 3: Создать Secret с токеном для сервисного аккаунта

Создайте файл `oke-kubeconfig-sa-token.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: oke-kubeconfig-sa-token
  namespace: kube-system
  annotations:
    kubernetes.io/service-account.name: kubeconfig-sa
type: kubernetes.io/service-account-token
```

Примените:

```powershell
kubectl apply -f oke-kubeconfig-sa-token.yaml
```

## Шаг 4: Получить токен и CA

**Токен (PowerShell):**

```powershell
$token = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl -n kube-system get secret oke-kubeconfig-sa-token -o jsonpath='{.data.token}')))
$token
```

**Токен (Bash / WSL):**

```bash
TOKEN=$(kubectl -n kube-system get secret oke-kubeconfig-sa-token -o jsonpath='{.data.token}' | base64 -d)
echo $TOKEN
```

**CA в base64 (для kubeconfig) — PowerShell:**

```powershell
kubectl -n kube-system get secret oke-kubeconfig-sa-token -o jsonpath='{.data.ca\.crt}'
```

Скопируйте вывод (одна строка base64).

**CA в base64 — Bash:**

```bash
kubectl -n kube-system get secret oke-kubeconfig-sa-token -o jsonpath='{.data.ca\.crt}'
```

## Шаг 5: Собрать kubeconfig вручную

Подставьте свои значения:

- **SERVER** — адрес API кластера, например `https://151.145.94.44:6443`
- **CA_BASE64** — строка из шага 4 (certificate-authority-data)
- **TOKEN** — значение токена из шага 4 (расшифрованный)

Создайте файл `kubeconfig-ci.yaml`:

```yaml
apiVersion: v1
kind: Config
clusters:
  - name: oke-cluster
    cluster:
      server: https://151.145.94.44:6443
      certificate-authority-data: <CA_BASE64>
users:
  - name: kubeconfig-sa
    user:
      token: <TOKEN>
contexts:
  - name: default
    context:
      cluster: oke-cluster
      user: kubeconfig-sa
current-context: default
```

Замените `<CA_BASE64>` и `<TOKEN>` на реальные значения. В `server:` укажите ваш URL API.

## Шаг 6: Закодировать в base64 и положить в GitHub

**PowerShell:**

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("kubeconfig-ci.yaml"))
```

**Bash:**

```bash
base64 -w 0 kubeconfig-ci.yaml
```

Скопируйте вывод целиком → в GitHub: **Settings** → **Secrets and variables** → **Actions** → **New repository secret** → имя **KUBE_CONFIG_BASE64**, значение — вставленная строка.

## Проверка

Локально (после сохранения в `~/.kube/config` или с `$env:KUBECONFIG="kubeconfig-ci.yaml"`):

```powershell
kubectl get nodes
```

Если команда выполняется без ошибок, тот же kubeconfig можно использовать в CI.

## Отзыв доступа

Чтобы отозвать доступ этого токена:

```powershell
kubectl -n kube-system delete secret oke-kubeconfig-sa-token
```

После этого обновите kubeconfig в секрете GitHub (новый токен или другой способ доступа).
