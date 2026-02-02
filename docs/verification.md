# Инструкция по проверке работоспособности

## Быстрая проверка (все сервисы подняты)

1. **Стартовая страница (frontend)**  
   Откройте в браузере: **http://localhost:8000/**  
   Должна открыться форма: выбор года, месяца, студента, поля GrammarE/ReadingE/…/WritingH, «Number of hours studied», кнопки «Send data» и «Print report».

2. **Health**  
   В браузере или curl:
   ```bash
   curl http://localhost:8000/health
   ```
   Ожидается: `{"status":"ok","database":"ok"}` (при доступной MySQL). Если БД недоступна: `"database":"error"`, `"status":"degraded"`.

3. **Список студентов**  
   ```bash
   curl http://localhost:8000/api/students
   ```
   Ожидается: JSON-массив `[]` или список студентов.

4. **Добавление студента**  
   ```bash
   curl -X POST http://localhost:8000/api/students \
     -H "Content-Type: application/json" \
     -d "{\"first_name\":\"Иван\",\"last_name\":\"Петров\"}"
   ```
   Ожидается: ответ 201 и JSON с полями `id`, `first_name`, `last_name`, `full_name`.

5. **Отправка данных занятия (Send data)**  
   В форме выберите год, месяц, студента, заполните поля и нажмите **Send data** — должно появиться сообщение «Данные сохранены».  
   Или через API:
   ```bash
   curl -X POST http://localhost:8000/api/lessons \
     -H "Content-Type: application/json" \
     -d "{\"student_id\":1,\"year\":2025,\"month\":1,\"grammar_e\":\"\",\"reading_e\":\"\",\"speaking_e\":\"\",\"writing_e\":\"\",\"grammar_h\":\"\",\"reading_h\":\"\",\"speaking_h\":\"\",\"writing_h\":\"\",\"hours_studied\":2}"
   ```
   Ожидается: 201 и JSON записи.

6. **Загрузка данных для формы**  
   Смените в форме год/месяц/студента — если для этой комбинации уже есть запись, поля должны подставиться автоматически (запрос к GET `/api/lessons?student_id=…&year=…&month=…`).

7. **Print report (PDF)**  
   Выберите студента, год и месяц, для которых есть сохранённые данные, нажмите **Print report**. Откроется новая вкладка со скачиванием PDF (если настроен шаблон report_template.docx и LibreOffice в контейнере).  
   Или: `curl -o report.pdf "http://localhost:8000/api/report/pdf?student_id=1&year=2025&month=1"`

8. **Метрики Prometheus**  
   ```bash
   curl http://localhost:8000/metrics
   ```
   Ожидается: текст в формате Prometheus (строки вида `# TYPE ...`, `...`).

9. **Документация API**  
   - Swagger UI: **http://localhost:8000/docs**  
   - ReDoc: **http://localhost:8000/redoc**

## Критерии по ТЗ

- Рабочий web-интерфейс — форма на `/` с выбором года/месяца/студента, полями и кнопками.  
- Взаимодействие frontend и backend — запросы к `/api/students`, `/api/lessons`, `/api/report/pdf`.  
- Работа backend с хранилищем данных — данные сохраняются и читаются из MySQL.  
- Остальные пункты (CI/CD, Kubernetes, Terraform, мониторинг) проверяются по соответствующим разделам README и документации.
