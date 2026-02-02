# Система учёта занятий по английскому языку

Финальный индивидуальный проект по курсу DevOps: web-приложение для учёта занятий по английскому для студентов с контейнеризацией, CI/CD, Kubernetes, Terraform, мониторингом и логированием.

## Архитектура

Подробная схема: [docs/architecture.md](docs/architecture.md).

```
Frontend (HTML/CSS/JS) → Backend (FastAPI) → MySQL
                              ↓
                    PDF-отчёт из шаблона .docx (LibreOffice)
```

- **Frontend**: форма выбора года/месяца/студента, поля занятий (English/Hebrew), кнопки «Send data» и «Print report». Взаимодействие с backend по HTTP.
- **Backend**: FastAPI, операции с MySQL, генерация PDF по шаблону .docx. Endpoints: `/health`, `/api/students`, `/api/lessons`, `/api/report/pdf`, `/metrics`.
- **Хранилище**: MySQL — студенты и записи занятий (месяц, год, оценки, часы).

## Структура репозитория

```
project/
├── backend/                 # FastAPI backend + раздача frontend
│   ├── app/
│   │   ├── main.py          # Точка входа, роутеры, статика, метрики
│   │   ├── config.py        # Настройки из env (12-factor)
│   │   ├── database.py      # SQLAlchemy, MySQL
│   │   ├── deps.py          # FastAPI dependencies (get_db)
│   │   ├── logging_config.py
│   │   ├── models/          # Student, LessonRecord
│   │   ├── routers/         # health, students, lessons, report
│   │   ├── schemas/         # Pydantic
│   │   └── services/        # Генерация PDF из .docx
│   ├── static/              # Frontend: index.html, css/, js/
│   ├── templates/           # Шаблон report_template.docx
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                # Исходники формы (копия в backend/static для сборки)
├── helm/english-lessons/    # Helm chart: Deployment, Service, Ingress (опц.)
├── terraform/               # IaC: EKS + RDS (структура, см. terraform/README.md)
├── .github/workflows/       # CI/CD: сборка образа, push в GHCR, Helm deploy
├── docs/                    # Инструкции по развёртыванию и проверке
└── README.md
```

## Развёртывание с нуля

### Режим разработки (код и статика с хоста, без пересборки)

Чтобы менять код и форму на лету без перезапуска контейнера:

1. В корне проекта создайте `.env` из примера:  
   `cp .env.example .env`  
   В нём задано `COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml` — подключается `docker-compose.dev.yml` с монтированием `backend/app`, `backend/static`, `backend/templates` и запуском uvicorn с `--reload`.
2. Запуск: `docker compose up -d` (или без `-d`).  
   После правок в HTML/CSS/JS достаточно обновить страницу в браузере; при изменении Python-кода uvicorn перезапустит приложение сам.

Без этого `.env` (или с пустым `COMPOSE_FILE`) выполняется только `docker-compose.yml`: образ собирается с копией кода внутри, пересборка образа нужна при каждом изменении.

### Требования

- **Python 3.12** (для локального запуска backend без Docker)
- Docker, Docker Compose (или Kubernetes + Helm)
- MySQL 8.x (или развёрнутая через Terraform)
- Для генерации PDF в backend-контейнере установлен LibreOffice (уже в Dockerfile)

### 1. База данных MySQL

Создайте БД и пользователя:

```sql
CREATE DATABASE english_lessons CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'app'@'%' IDENTIFIED BY 'your_password';
GRANT ALL ON english_lessons.* TO 'app'@'%';
FLUSH PRIVILEGES;
```

Таблицы `students` и `lesson_records` создаются при первом запуске backend (init_db).

### 2. Backend локально (без Docker)

```bash
cd backend
cp .env.example .env
# Отредактируйте .env: MYSQL_HOST, MYSQL_PASSWORD и т.д.
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Для генерации PDF локально нужен LibreOffice в PATH (или только тестирование API без PDF).

### 3. Backend в Docker

```bash
cd backend
docker build -t english-lessons-api:latest .
docker run --rm -p 8000:8000 \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_PASSWORD=your_password \
  -e MYSQL_DATABASE=english_lessons \
  english-lessons-api:latest
```

### 4. Frontend

Форма раздаётся тем же backend: откройте в браузере **http://localhost:8000/** — выбор года/месяца/студента, поля GrammarE/ReadingE/…/WritingH, часы 1–12, кнопки **Send data** и **Print report**.

### 5. Kubernetes (Helm)

После подготовки кластера (Terraform) и registry:

```bash
helm install english-lessons ./helm/english-lessons \
  --set image.repository=your-registry/english-lessons-api \
  --set mysql.host=your-mysql-host \
  --set mysql.password=...
```

Подробнее: [docs/deployment.md](docs/deployment.md).

## Проверка работоспособности

1. **Стартовая страница**: откройте **http://localhost:8000/** — форма учёта занятий.
2. **Health**: `GET http://localhost:8000/health` — ответ `{"status":"ok","database":"ok"}` при доступной MySQL.
3. **Список студентов**: `GET http://localhost:8000/api/students` — JSON-массив (изначально пустой).
4. **Добавить студента**: `POST http://localhost:8000/api/students` с телом `{"first_name":"Иван","last_name":"Петров"}`.
5. **Send data** в форме или `POST http://localhost:8000/api/lessons` с телом по схеме (student_id, year, month, grammar_e, … hours_studied).
6. **Print report**: кнопка в форме или `GET http://localhost:8000/api/report/pdf?student_id=1&year=2025&month=1` — скачивание PDF (нужен шаблон report_template.docx и LibreOffice в контейнере).
7. **Метрики Prometheus**: `GET http://localhost:8000/metrics`.

Подробнее: [docs/verification.md](docs/verification.md).

## Документация API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## DevOps (по ТЗ)

- **Контейнеризация**: Dockerfile для backend, образ в registry (Docker Hub / GHCR).
- **CI/CD**: GitHub Actions — сборка образа, публикация в registry, деплой в Kubernetes/Helm.
- **IaC**: Terraform — кластер (EKS/AKS), ресурсы для БД.
- **Kubernetes/Helm**: Deployment, Service; опционально Ingress, ArgoCD.
- **Мониторинг и логи**: Prometheus (метрики `/metrics`), Grafana, Loki + Promtail (логи в JSON при `LOG_FORMAT=json`).

## Лицензия

Учебный проект.
