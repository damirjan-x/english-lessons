# Backend: FastAPI + MySQL, генерация PDF из .docx (LibreOffice)
# Multi-stage для уменьшения размера образа (опционально — один этап для простоты)

FROM python:3.12-slim

# LibreOffice для конвертации .docx -> .pdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    libreoffice-common \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения и frontend (статическая форма)
COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/

# Переменные для продакшена (переопределяются в K8s)
ENV PYTHONUNBUFFERED=1
ENV LOG_FORMAT=json
EXPOSE 8000

# Запуск через uvicorn (K8s-ready: один воркер по умолчанию)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
