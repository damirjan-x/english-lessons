# Grafana и Prometheus в кластере OKE

Приложение отдаёт метрики Prometheus на `GET /metrics`. Чтобы смотреть их в Grafana, в кластер нужно поставить Prometheus (сбор метрик) и Grafana (дашборды).

## 1. Установка Prometheus и Grafana (Helm)

Добавьте репозитории и создайте namespace:

```powershell
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

kubectl create namespace monitoring
```

**Prometheus** (минимальный набор, без лишних компонентов):

```powershell
helm install prometheus prometheus-community/prometheus -n monitoring `
  --set server.persistentVolume.enabled=false `
  --set alertmanager.enabled=false `
  --set prometheus-pushgateway.enabled=false `
  --set prometheus-node-exporter.enabled=false `
  --set kube-state-metrics.enabled=false
```

**Grafana** (пароль администратора задайте свой):

```powershell
helm install grafana grafana/grafana -n monitoring `
  --set adminPassword=admin `
  --set service.type=ClusterIP
```

## 2. Аннотации на сервисе приложения

Чарт `english-lessons` уже добавляет аннотации для автообнаружения Prometheus. Если релиз ставили до этого — обновите его, чтобы подхватить аннотации:

```powershell
helm upgrade english-lessons ./helm/english-lessons -n english-lessons --reuse-values
```

Проверьте, что у Service есть аннотации:

```powershell
kubectl get svc english-lessons -n english-lessons -o yaml | findstr prometheus
```

Должны быть: `prometheus.io/scrape: "true"`, `prometheus.io/port: "8000"`, `prometheus.io/path: "/metrics"`.

## 3. Доступ к Grafana

Проброс порта на локальную машину:

```powershell
kubectl port-forward -n monitoring svc/grafana 3000:80
```

В браузере откройте **http://localhost:3000**. Логин: **admin**, пароль: тот, что задали в `adminPassword` (по умолчанию в команде выше — `admin`).

## 4. Источник данных Prometheus в Grafana

1. **Connections** → **Data sources** → **Add data source**.
2. Выберите **Prometheus**.
3. **URL**: `http://prometheus-server.monitoring.svc.cluster.local` (сервис Prometheus в namespace `monitoring`).
4. **Save & test** — должно быть зелёное «Data source is working».

## 5. Дашборд по метрикам приложения

1. **Create** → **Import dashboard**.
2. Введите ID дашборда **3662** (Prometheus 2.0 Overview) или **7362** (FastAPI / Python) и нажмите **Load**.
3. Выберите источник **Prometheus** → **Import**.

Либо создайте свой дашборд: **Create** → **Dashboard** → **Add visualization**. В запросе укажите метрики с префиксом `python_` или `http_` (например `http_requests_total`), если приложение их отдаёт.

## 6. Проверка сбора метрик приложения

В Prometheus можно проверить таргеты: откройте UI Prometheus (port-forward к `prometheus-server` на порт 9090) и в **Status** → **Targets** найдите job по сервису `english-lessons`. Либо в Grafana: **Explore** → выберите Prometheus → запрос `up{job="english-lessons"}` или `python_info`.

## 7. Диагностика: данные не видны, выпадающий список «cluster» пуст

Проверьте цепочку **кластер → Prometheus → Grafana** по шагам.

### Шаг 1: Prometheus собирает таргеты

Откройте UI Prometheus из кластера:

```powershell
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
```

В браузере: **http://localhost:9090**. Если Prometheus слушает на 80, то откроется веб-интерфейс (иногда нужен путь `/`, реже порт в chart — 80).

Перейдите в **Status** → **Targets**. Должны быть таргеты (например `kubernetes-service-endpoints` или job с namespace `english-lessons`). Состояние **UP** — скрейп работает; **Down** — проверьте, что поды приложения запущены и у Service есть аннотации (раздел 2 выше).

Проверка метрик напрямую в Prometheus: вкладка **Graph**, запрос `up` — должны быть линии по таргетам. Запрос `http_requests_total` покажет метрики приложения, если скрейп настроен и приложение отдаёт `/metrics`.

### Шаг 2: Grafana видит Prometheus

В Grafana: **Connections** → **Data sources**. Выберите добавленный Prometheus и нажмите **Save & test**. Должно быть «Data source is working». Если ошибка — проверьте URL: `http://prometheus-server.monitoring.svc.cluster.local` (из того же кластера).

### Шаг 3: Запрос в Explore (без дашборда)

**Explore** → вверху выберите источник **Prometheus** → введите запрос и нажмите **Run query**:

- `up` — все таргеты (должны быть точки/линии);
- `up{namespace="english-lessons"}` — только приложение;
- `http_requests_total` — метрики API (появятся после деплоя приложения с метриками).

Если здесь данные есть — источник данных работает, проблема только в дашборде или переменных.

### Почему выпадающий список «cluster» пустой

В импортированных дашбордах (например 3662, 7362) переменные (cluster, job, instance) строятся по меткам Prometheus. Если у ваших метрик другие имена меток или скрейп идёт через `kubernetes-service-endpoints`, переменная может запрашивать несуществующий label — список будет пуст.

Что сделать:

1. В **Explore** выполните `up` и посмотрите, какие **labels** возвращает Prometheus (job, namespace, instance, cluster и т.д.).
2. Откройте дашборд → **Dashboard settings** (шестерёнка) → **Variables**. Найдите переменную «cluster» (или аналогичную) и посмотрите **Query**. Подправьте запрос под ваши метки (например `label_values(up, namespace)` или `label_values(up, job)`), затем сохраните дашборд.
3. Либо создайте свой дашборд: **Dashboards** → **New** → **Add visualization**, выберите Prometheus и запросы вроде `http_requests_total`, `rate(http_request_duration_seconds_count[5m])` — без переменных всё будет видно сразу.

## Кратко

| Действие              | Команда / URL |
|-----------------------|----------------|
| Установить Prometheus | `helm install prometheus ...` (см. выше) |
| Установить Grafana    | `helm install grafana ...` (см. выше) |
| Открыть Grafana       | `kubectl port-forward -n monitoring svc/grafana 3000:80` → http://localhost:3000 |
| Источник данных       | Prometheus, URL: `http://prometheus-server.monitoring.svc.cluster.local` |

Метрики приложения доступны на **http://english-lessons.english-lessons.svc.cluster.local:8000/metrics** изнутри кластера; Prometheus скрейпит их по аннотациям на Service.
