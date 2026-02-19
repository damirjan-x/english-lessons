# Backend: FastAPI + MySQL, генерация PDF из .docx (LibreOffice)
# Используется в CI/CD: context=./backend, file=./Dockerfile (пути COPY — относительно backend/)

FROM python:3.12-slim

# LibreOffice для конвертации .docx -> .pdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    libreoffice-common \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Зависимости (контекст сборки — backend/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения и frontend (статическая форма)
COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/

ENV PYTHONUNBUFFERED=1
ENV LOG_FORMAT=json
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
