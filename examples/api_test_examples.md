# Ejemplos de Requests para Testear la API de AI Data Platform

## Documentación interactiva
- [Swagger UI](http://localhost:8001/docs)

---

## 1. Health Check
```bash
curl http://localhost:8001/health
```

## 2. Obtener información de la API
```bash
curl http://localhost:8001/
```

## 3. Ingesta de datos (ETL)
```bash
curl -X POST http://localhost:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "csv_file_path": "data/ads_spend.csv",
    "batch_id": "batch-001",
    "skip_if_exists": true,
    "validation_threshold": 95.0
  }'
```

## 4. Métricas generales (CAC, ROAS)
```bash
curl "http://localhost:8001/metrics?start_date=2025-06-01&end_date=2025-06-30"
```

## 5. Métricas por plataforma
```bash
curl "http://localhost:8001/platform-metrics?start_date=2025-06-01&end_date=2025-06-30"
```

## 6. Análisis temporal (comparación periodos)
```bash
curl http://localhost:8001/time-analysis
```

## 7. Tendencias diarias (últimos 30 días)
```bash
curl "http://localhost:8001/daily-trends?days=30"
```

## 8. Consulta en lenguaje natural (NLQ)
```bash
curl -X POST http://localhost:8001/nlq \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me daily metrics for last month"
  }'
```

---

# Equivalencia CLI vs API

| Funcionalidad CLI                      | Endpoint API                | Notas |
|----------------------------------------|-----------------------------|-------|
| Ingesta de datos (etl_pipeline)        | POST /ingest                | Sí    |
| Métricas generales                     | GET /metrics                | Sí    |
| Métricas por plataforma                | GET /platform-metrics       | Sí    |
| Análisis temporal                      | GET /time-analysis          | Sí    |
| Tendencias diarias                     | GET /daily-trends           | Sí    |
| Consulta NLQ                           | POST /nlq                   | Sí    |
| SQL predefinido                        | Solo CLI (`cli sql`)        | No API|
| Gestión workflows n8n (setup, status)  | Solo CLI (`cli n8n ...`)    | No API|
| Info/configuración plataforma           | Solo CLI (`cli info`)       | No API|

- Todo lo esencial para análisis y ETL está disponible vía API.
- Operaciones administrativas y SQL avanzadas solo por CLI.
