# Инструкция по развёртыванию проекта с нуля

## Требования

- Docker и Docker Compose (или доступ к Kubernetes-кластеру)
- MySQL 8.x (локально, в Docker или в облаке — RDS/Azure DB)
- Для K8s: kubectl, Helm 3
- Для CI/CD: репозиторий на GitHub

## Вариант 1: Локально через Docker Compose

1. Клонируйте репозиторий и перейдите в корень проекта.

2. **Режим разработки (рекомендуется):** скопируйте `.env.example` в `.env`. В нём задано `COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml` — при `docker compose up` монтируются каталоги `backend/app`, `backend/static`, `backend/templates`, изменения кода и формы видны без пересборки образа; uvicorn запускается с `--reload`.

3. Запустите сервисы:
   ```bash
   docker compose up -d
   ```
   Поднимутся MySQL (порт 3306) и backend (порт 8000).

4. Откройте в браузере: **http://localhost:8000/** — форма учёта занятий.

5. Добавьте первого студента через API или позже через форму (после добавления эндпоинта создания студента в UI можно использовать `/docs` → POST `/api/students`).

## Вариант 2: Сборка образа backend вручную

1. Соберите образ из каталога backend:
   ```bash
   cd backend
   docker build -t english-lessons-api:latest .
   ```

2. Запустите MySQL (например, `docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=english_lessons mysql:8.0` или используйте существующий инстанс).

3. Запустите backend:
   ```bash
   docker run --rm -p 8000:8000 \
     -e MYSQL_HOST=host.docker.internal \
     -e MYSQL_PASSWORD=your_password \
     -e MYSQL_DATABASE=english_lessons \
     english-lessons-api:latest
   ```
   На Linux вместо `host.docker.internal` укажите IP хоста или имя сервиса MySQL в одной сети.

## Вариант 3: Развёртывание в Kubernetes (Helm)

1. Подготовьте кластер (например, через Terraform — см. `terraform/README.md`) и получите kubeconfig.

2. Создайте namespace (по желанию):
   ```bash
   kubectl create namespace english-lessons
   ```

3. Убедитесь, что MySQL доступна из кластера (внутренний сервис или внешний хост). При необходимости создайте Secret с паролем:
   ```bash
   kubectl create secret generic mysql-credentials \
     --from-literal=mysql-password=YOUR_PASSWORD \
     -n english-lessons
   ```

4. Установите Helm chart:
   ```bash
   helm install english-lessons ./helm/english-lessons \
     --namespace english-lessons \
     --set image.repository=ghcr.io/YOUR_ORG/english-lessons-api \
     --set image.tag=latest \
     --set mysql.host=your-mysql-host \
     --set mysql.existingSecret=mysql-credentials
   ```

5. Проверьте поды и сервис:
   ```bash
   kubectl get pods,svc -n english-lessons
   ```

6. Доступ к приложению: port-forward или включите Ingress в `values.yaml` и настройте хост.

## Вариант 4: CI/CD (GitHub Actions)

1. В репозитории GitHub добавьте секреты:
   - Для деплоя в K8s: `KUBE_CONFIG_BASE64` (base64-encoded kubeconfig).
   - Для подключения к MySQL из пода: `MYSQL_HOST`, `MYSQL_PASSWORD`.

2. При пуше в ветку `main`/`master` workflow:
   - собирает Docker-образ из `backend/`;
   - пушит образ в GitHub Container Registry (ghcr.io);
   - при наличии секретов выполняет `helm upgrade --install` для деплоя в кластер.

3. Если кластер ещё не настроен, шаг деплоя можно отключить (убрать job `deploy` или условие `if`), чтобы работала только сборка и публикация образа.

## Шаблон отчёта (PDF)

Чтобы кнопка «Print report» возвращала PDF, поместите файл **report_template.docx** в каталог `backend/templates/` (с плейсхолдерами по `backend/templates/README.md`) и пересоберите образ. В контейнере уже установлен LibreOffice для конвертации docx → pdf.
