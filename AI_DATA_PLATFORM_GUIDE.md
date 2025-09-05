# 🚀 AI Data Platform - Guía Completa del Sistema

## 📊 **Descripción General**
El AI Data Platform es un sistema completo de analytics que procesa datos de advertising (Google Ads, Meta Ads) y proporciona métricas, análisis temporal y consultas inteligentes a través de una interfaz web intuitiva.

---

## 🎯 **Funcionalidades Principales**

### 1. **📈 Dashboard de Métricas (Analytics Dashboard)**
Métricas automáticas para períodos específicos con KPIs clave.

#### **Métricas Disponibles:**
- **Total Spend**: Gasto total en publicidad
- **Total Conversions**: Número total de conversiones
- **Total Revenue**: Ingresos totales generados
- **CAC (Customer Acquisition Cost)**: Costo por adquisición de cliente
- **ROAS (Return on Ad Spend)**: Retorno de inversión publicitaria

#### **Ejemplo de Resultados (Junio 2025):**
```
📊 Métricas de Junio 2025:
• Total Spend: $7,695,976.05
• Total Conversions: 258,174
• Total Revenue: $25,817,400.00
• CAC: $29.81
• ROAS: 3.35x
```

### 2. **🔍 Métricas por Plataforma**
Desglose detallado del rendimiento por plataforma publicitaria.

#### **Plataformas Soportadas:**
- Google Ads
- Meta (Facebook/Instagram)

#### **Ejemplo de Consulta:**
```
📱 Métricas por Plataforma (Junio 2025):
• Google: $3,940,456.68
• Meta: $3,755,519.37
```

### 3. **⏰ Análisis Temporal (Time Analysis)**
Comparación automática entre períodos para identificar tendencias.

#### **Comparaciones Disponibles:**
- Último mes vs mes anterior
- Últimos 30 días vs 30 días previos
- Períodos personalizados

#### **Métricas de Comparación:**
- Crecimiento en spend
- Variación en conversiones
- Cambios en ROAS
- Tendencias por plataforma

---

## 💾 **Ingestion de Datos**

### **Métodos Disponibles:**
1. **Manual**: Botón "Ingest Data" en la interfaz
2. **n8n Workflow**: Automatización completa
3. **Webhook**: Integración con sistemas externos

#### **Proceso de Ingestion:**
1. Lee archivo CSV (`ads_spend.csv`)
2. Valida y transforma datos
3. Carga a base de datos DuckDB
4. Actualiza métricas automáticamente

#### **Datos Procesados:**
- 52,000+ registros actuales
- Rango: Enero 2025 - Junio 2025
- Campos: fecha, plataforma, gasto, clicks, impresiones, conversiones

---

## 🛠️ **SQL Query Interface**

### **Capacidades:**
- Consultas SQL libres sobre la base de datos
- Tabla principal: `raw_ads_spend`
- Resultados en tiempo real

### **📝 Ejemplos de Consultas SQL para el Video:**

#### **1. Top Plataformas por Gasto (Junio 2025):**
```sql
SELECT platform, SUM(spend) as total_spend 
FROM raw_ads_spend 
WHERE date >= '2025-06-01' AND date <= '2025-06-30' 
GROUP BY platform 
ORDER BY total_spend DESC 
LIMIT 10
```

#### **2. Rendimiento Diario (Última Semana):**
```sql
SELECT date, 
       SUM(spend) as daily_spend,
       SUM(conversions) as daily_conversions,
       ROUND(SUM(conversions * 100.0) / SUM(spend), 2) as conversion_rate
FROM raw_ads_spend 
WHERE date >= '2025-06-24' AND date <= '2025-06-30'
GROUP BY date 
ORDER BY date DESC
```

#### **3. Análisis por País y Dispositivo:**
```sql
SELECT country, device, 
       COUNT(*) as campaigns,
       SUM(spend) as total_spend,
       AVG(spend/clicks) as avg_cpc
FROM raw_ads_spend 
WHERE date >= '2025-06-01' 
GROUP BY country, device 
HAVING SUM(spend) > 10000
ORDER BY total_spend DESC
```

#### **4. Métricas de Eficiencia por Campaña:**
```sql
SELECT campaign, platform,
       SUM(spend) as spend,
       SUM(conversions) as conversions,
       ROUND(SUM(spend) / SUM(conversions), 2) as cac,
       ROUND(SUM(conversions * 100.0) / SUM(spend), 2) as roas
FROM raw_ads_spend 
WHERE date >= '2025-06-01' AND date <= '2025-06-30'
GROUP BY campaign, platform
HAVING SUM(conversions) > 100
ORDER BY roas DESC
LIMIT 15
```

#### **5. Tendencia Semanal de Gasto:**
```sql
SELECT EXTRACT(WEEK FROM date) as week_number,
       SUM(spend) as weekly_spend,
       COUNT(DISTINCT campaign) as active_campaigns,
       AVG(spend/impressions * 1000) as avg_cpm
FROM raw_ads_spend 
WHERE date >= '2025-05-01' AND date <= '2025-06-30'
GROUP BY EXTRACT(WEEK FROM date)
ORDER BY week_number
```

---

## 🤖 **Natural Language Query (NLQ)**

### **Capacidades Actuales:**
- Convierte preguntas en lenguaje natural a SQL
- Interfaz intuitiva para usuarios no técnicos
- Respuestas automáticas basadas en datos

### **📢 Ejemplos de Preguntas para el Video:**

#### **Preguntas Básicas:**
```
1. "¿Cuánto gastamos en Google en junio?"
2. "¿Cuál plataforma tuvo más conversiones?"
3. "¿Cómo fue el ROAS en mayo vs junio?"
4. "¿Qué campaña tuvo mejor rendimiento?"
5. "¿En qué país gastamos más dinero?"
```

#### **Preguntas Avanzadas:**
```
6. "¿Cuál es la tendencia de gasto por semana en los últimos 2 meses?"
7. "¿Qué dispositivos generan mejor ROI en Meta?"
8. "¿Cuál es el CAC promedio por país en Google?"
9. "¿Cómo se compara el CPM entre plataformas?"
10. "¿Qué campaña tiene el mejor ratio conversión/gasto?"
```

#### **Preguntas de Análisis:**
```
11. "¿Hay correlación entre gasto e impresiones?"
12. "¿Qué día de la semana es más eficiente para las campañas?"
13. "¿Cuál es la distribución de gasto por mes?"
14. "¿Qué cuentas publicitarias son más rentables?"
15. "¿Cómo varía el CPC por dispositivo y país?"
```

---

## 🎛️ **n8n Workflow Automation**

### **Funcionalidades Actuales:**
- **Setup Workflow**: Crea y activa workflows automáticamente
- **Webhook Trigger**: Permite disparar procesos desde sistemas externos
- **Manual Trigger**: Ejecución manual desde interfaz n8n

### **URL del Webhook:**
```
http://localhost:5678/webhook/trigger-ingestion
```

### **Flujo de Automatización:**
1. Webhook recibe trigger
2. Llama API de ingestion (`/ingest`)
3. Procesa CSV automáticamente
4. Retorna confirmación de éxito

---

## 🗂️ **Estructura de Datos**

### **Tabla Principal: `raw_ads_spend`**
```sql
Columnas disponibles:
• date (DATE) - Fecha de la campaña
• platform (VARCHAR) - Google/Meta
• account (VARCHAR) - Cuenta publicitaria
• campaign (VARCHAR) - Nombre de campaña
• country (VARCHAR) - País objetivo
• device (VARCHAR) - Desktop/Mobile/Tablet
• spend (DECIMAL) - Gasto en USD
• clicks (INTEGER) - Número de clicks
• impressions (INTEGER) - Impresiones
• conversions (INTEGER) - Conversiones
• load_date (TIMESTAMP) - Fecha de carga
• source_file_name (VARCHAR) - Archivo origen
• batch_id (VARCHAR) - ID del lote
```

### **Tablas Auxiliares:**
- `daily_metrics` - Métricas diarias agregadas
- `platform_performance` - Rendimiento por plataforma
- `kpi_metrics` - KPIs calculados
- `data_quality_summary` - Resumen de calidad de datos

---

## 🌐 **URLs de Acceso**

```
• Dashboard Principal: http://localhost:8501
• API Documentation: http://localhost:8001/docs
• n8n Interface: http://localhost:5678
• Webhook Endpoint: http://localhost:5678/webhook/trigger-ingestion
```

---

## 📱 **Demo Script para Video**

### **Sección 1: Dashboard Overview (2-3 min)**
1. Mostrar dashboard principal
2. Explicar métricas de Junio 2025
3. Mostrar análisis temporal
4. Demostrar métricas por plataforma

### **Sección 2: SQL Interface (3-4 min)**
1. Ejecutar query de top plataformas
2. Mostrar análisis por país/dispositivo
3. Demostrar métricas de eficiencia
4. Explicar flexibilidad de consultas

### **Sección 3: Natural Language Query (2-3 min)**
1. Preguntas básicas sobre gasto
2. Consultas de tendencias
3. Análisis comparativo
4. Mostrar facilidad de uso

### **Sección 4: Automatización n8n (2-3 min)**
1. Mostrar setup de workflow
2. Demostrar ingestion automática
3. Explicar webhook integration
4. Mostrar confirmación de procesos

### **Sección 5: Data Ingestion (1-2 min)**
1. Demostrar carga manual
2. Mostrar resultado de processing
3. Verificar actualización de métricas

---

## 🎯 **Casos de Uso Principales**

1. **📊 Reporte Diario de Performance**
2. **📈 Análisis de Tendencias Mensual** 
3. **💰 Optimización de Budget por Plataforma**
4. **🎯 Identificación de Campañas Top/Bottom**
5. **🌍 Análisis Geográfico de Rendimiento**
6. **📱 Comparación de Performance por Dispositivo**
7. **🔄 Automatización de Reportes via Webhook**

---

*¡El sistema está listo para demostrar toda su potencia en el video! 🚀*
