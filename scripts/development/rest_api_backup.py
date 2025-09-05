
# --- IMPORTS & APP DEFINITION MUST BE AT THE TOP ---
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import logging
from ..database.connection import db
from ..analytics.kpi_engine import KPIEngine
from ..analytics.time_analysis import TimeAnalysisEngine
from ..analytics.nlq import execute_nlq
from ..analytics.sql_queries import sql_interface
from ..api.n8n_api_client import N8nAPIClient
from ..config import settings
from ..ingestion.etl_pipeline import run_etl_pipeline

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Data Platform API",
    description="REST API for accessing marketing KPI metrics and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
kpi_engine = None
time_analysis_engine = None

# --- END IMPORTS & APP DEFINITION ---

# Utilidad para obtener cliente n8n
def get_n8n_client(api_key: str = None):
    key = api_key or settings.n8n.api_key or "aiplatform2024"
    return N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=key,
        webhook_secret=settings.n8n.webhook_secret
    )

# 5. ETL directo (sin n8n)
@app.post("/etl-direct")
async def etl_direct(payload: Dict[str, Any] = Body(...)):
    """
    Run ETL pipeline directly (without n8n). Body: {"csv_file_path": "..."}
    """
    from ..ingestion.etl_pipeline import ETLPipeline
    csv_file_path = payload.get("csv_file_path") or str(settings.data.input_directory) + "/ads_spend.csv"
    try:
        pipeline = ETLPipeline(csv_file_path)
        result = pipeline.run()
        if result.success:
            summary = result.get_summary()
            return {"success": True, "summary": summary}
        else:
            return {"success": False, "error": result.error_message}
    except Exception as e:
        logger.error(f"Error running ETL direct: {e}")
        return {"success": False, "error": str(e)}

# 1. Setup workflow
@app.post("/n8n/setup")
async def n8n_setup(payload: Dict[str, Any] = Body(...)):
    """
    Set up n8n data ingestion workflow. Body: {"api_key": "...", "csv_file_path": "..."}
    """
    api_key = payload.get("api_key")
    csv_file_path = payload.get("csv_file_path", "ads_spend.csv")
    client = get_n8n_client(api_key)
    workflow_id = client.setup_data_ingestion_workflow(csv_file_path)
    if workflow_id:
        return {"success": True, "workflow_id": workflow_id}
    return {"success": False, "error": "Failed to set up workflow"}

# 2. Test conexión n8n
@app.post("/n8n/test")
async def n8n_test(payload: Dict[str, Any] = Body(...)):
    """
    Test connection to n8n instance. Body: {"api_key": "..."}
    """
    api_key = payload.get("api_key")
    client = get_n8n_client(api_key)
    ok = client.test_connection()
    return {"success": ok}

# 3. Status workflow
@app.post("/n8n/status")
async def n8n_status(payload: Dict[str, Any] = Body(...)):
    """
    Get current workflow status. Body: {"api_key": "...", "workflow_name": "..."}
    """
    api_key = payload.get("api_key")
    workflow_name = payload.get("workflow_name", "AI Data Platform - Data Ingestion")
    client = get_n8n_client(api_key)
    workflow = client.get_workflow_by_name(workflow_name)
    if not workflow:
        return {"success": False, "error": "Workflow not found"}
    workflow_id = workflow.get('id')
    status_info = client.get_workflow_status(workflow_id)
    executions = client.monitor_workflow_executions(workflow_id, limit=5)
    return {"success": True, "workflow": status_info, "executions": executions}

# 4. Ingest (trigger workflow)
@app.post("/n8n/ingest")
async def n8n_ingest(payload: Dict[str, Any] = Body(...)):
    """
    Trigger data ingestion workflow. Body: {"api_key": "...", "csv_file_path": "..."}
    """
    api_key = payload.get("api_key")
    csv_file_path = payload.get("csv_file_path", "ads_spend.csv")
    client = get_n8n_client(api_key)
    success = client.run_data_ingestion(csv_file_path)
    return {"success": success}

# 6. Platform info
@app.get("/platform-info")
async def platform_info():
    """
    Get platform configuration and status information.
    """
    try:
        info = {
            "app_name": settings.app_name,
            "version": settings.version,
            "environment": settings.environment,
            "database": {
                "path": settings.database.path,
                "timeout": settings.database.connection_timeout
            },
            "n8n": {
                "base_url": settings.n8n.base_url,
                "workflow_id": settings.n8n.workflow_id,
                "automation_enabled": settings.n8n.enable_automation
            },
            "data": {
                "input_directory": settings.data.input_directory,
                "output_directory": settings.data.output_directory
            },
            "features": {
                "enable_api": settings.enable_api,
                "enable_natural_language": settings.enable_natural_language,
                "enable_metrics_caching": settings.enable_metrics_caching
            }
        }
        return info
    except Exception as e:
        logger.error(f"Error getting platform info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get platform info")
"""
REST API for AI Data Platform
Provides endpoints for accessing KPI metrics and time-based analysis
"""
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import logging

from ..database.connection import db
from ..analytics.kpi_engine import KPIEngine
from ..analytics.time_analysis import TimeAnalysisEngine
from ..analytics.nlq import execute_nlq
from ..analytics.sql_queries import sql_interface
@app.post("/sql-query")
async def execute_sql_query(
    payload: Dict[str, Any] = Body(..., example={
        "query_name": "daily_metrics",
        "parameters": {"start_date": "2025-06-01", "end_date": "2025-06-30"},
        "format": "json"
    })
):
    """
    Execute a predefined SQL query by name with parameters.

    Body JSON parameters:
    - query_name: Name of the predefined query (see /sql-query-help)
    - parameters: Dict of parameters (e.g. start_date, end_date)
    - format: Output format (table, json, summary). Default: json
    """
    try:
        query_name = payload.get("query_name")
        parameters = payload.get("parameters", {})
        format_type = payload.get("format", "json")
        if not query_name:
            raise HTTPException(status_code=400, detail="query_name is required")
        result = sql_interface.execute_predefined_query(query_name, parameters)
        formatted = sql_interface.format_query_result(result, format_type)
        return {"success": result.success, "row_count": result.row_count, "data": result.data if format_type=="json" else formatted, "format": format_type, "error": result.error_message}
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute SQL query")

@app.get("/sql-query-help")
async def sql_query_help(query_name: Optional[str] = None):
    """
    Get help and list of available predefined SQL queries.
    Query param: query_name (optional)
    """
    try:
        help_text = sql_interface.get_query_help(query_name)
        return {"help": help_text}
    except Exception as e:
        logger.error(f"Error getting SQL query help: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SQL query help")
from ..config import settings
from ..ingestion.etl_pipeline import run_etl_pipeline

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Data Platform API",
    description="REST API for accessing marketing KPI metrics and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
kpi_engine = None
time_analysis_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize API components on startup"""
    global kpi_engine, time_analysis_engine
    
    try:
        # Initialize database connection
        db.connect()
        
        # Initialize analytics engines
        kpi_engine = KPIEngine(db)
        time_analysis_engine = TimeAnalysisEngine(db)
        
        logger.info("API startup completed successfully")
    except Exception as e:
        logger.error(f"API startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    try:
        db.disconnect()
        logger.info("API shutdown completed successfully")
    except Exception as e:
        logger.error(f"API shutdown error: {e}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Data Platform API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "metrics": "/metrics",
            "time-analysis": "/time-analysis",
            "daily-trends": "/daily-trends",
            "ingest": "/ingest",
            "nlq": "/nlq",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/metrics")
async def get_metrics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get CAC and ROAS metrics for a specified date range
    
    If no dates provided, returns metrics for the last 30 days of available data
    """
    try:
        if not kpi_engine:
            raise HTTPException(status_code=500, detail="KPI engine not initialized")
        
        # If no dates provided, use the last 30 days of available data
        if not start_date and not end_date:
            start_date = date(2025, 6, 1)
            end_date = date(2025, 6, 30)
        elif not end_date:
            end_date = start_date
        elif not start_date:
            start_date = end_date
        
        # Validate date range
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
        
        # Get metrics for the specified period
        metrics = kpi_engine.calculate_period_metrics(start_date, end_date)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@app.get("/time-analysis")
async def get_time_analysis():
    """
    Get period-over-period comparison analysis
    
    Compares the last 30 days vs prior 30 days of available data
    """
    try:
        if not time_analysis_engine:
            raise HTTPException(status_code=500, detail="Time analysis engine not initialized")
        
        # Get comparison results
        comparison = time_analysis_engine.analyze_last_30_days_vs_prior()
        
        return {
            "analysis": {
                "current_period": {
                    "label": comparison['current_period']['label'],
                    "start_date": comparison['current_period']['start_date'].isoformat(),
                    "end_date": comparison['current_period']['end_date'].isoformat()
                },
                "previous_period": {
                    "label": comparison['previous_period']['label'],
                    "start_date": comparison['previous_period']['start_date'].isoformat(),
                    "end_date": comparison['previous_period']['end_date'].isoformat()
                },
                "summary": comparison['summary'],
                "comparison": comparison['comparison']
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting time analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve time analysis")

@app.get("/daily-trends")
async def get_daily_trends(
    days: int = Query(30, ge=1, le=180, description="Number of days to analyze")
):
    """
    Get daily metrics trends for the specified number of days
    
    Returns daily CAC, ROAS, spend, and conversions for trend analysis
    """
    try:
        if not time_analysis_engine:
            raise HTTPException(status_code=500, detail="Time analysis engine not initialized")
        
        # Get daily trends
        daily_metrics = time_analysis_engine.get_daily_metrics_trend(days)
        
        return {
            "trends": {
                "days_analyzed": days,
                "daily_metrics": daily_metrics
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting daily trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve daily trends")

@app.get("/platform-metrics")
async def get_platform_metrics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get CAC and ROAS metrics broken down by platform
    
    If no dates provided, uses the last 30 days of available data
    """
    try:
        if not kpi_engine:
            raise HTTPException(status_code=500, detail="KPI engine not initialized")
        
        # If no dates provided, use the last 30 days of available data
        if not start_date and not end_date:
            start_date = date(2025, 6, 1)
            end_date = date(2025, 6, 30)
        elif not end_date:
            end_date = start_date
        elif not start_date:
            start_date = end_date
        
        # Get platform metrics
        platform_metrics = kpi_engine.calculate_platform_metrics(start_date, end_date)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "platform_metrics": platform_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting platform metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve platform metrics")

@app.post("/nlq")
async def natural_language_query(payload: Dict[str, Any]):
    """
    Execute a natural language query mapped to predefined SQL templates.

    Body JSON parameters:
    - question: The natural language question
    - start_date, end_date, previous_start_date, previous_end_date: optional filters
    """
    try:
        question = payload.get("question", "")
        result = execute_nlq(question, payload)
        status_code = 200 if result.get("success") else 400
        return JSONResponse(status_code=status_code, content=result)
    except Exception as e:
        logger.error(f"Error during NLQ execution: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute NLQ")

@app.post("/ingest")
async def ingest_data(payload: Dict[str, Any]):
    """
    Trigger ETL pipeline execution from n8n or external callers.

    Body JSON parameters:
    - csv_file_path: Path to CSV file (defaults to data/ads_spend.csv)
    - batch_id: Optional batch identifier
    - skip_if_exists: Optional bool (default True)
    - validation_threshold: Optional float percent (default 95.0)
    """
    try:
        csv_file_path = payload.get("csv_file_path") or str((settings.data.input_directory / "ads_spend.csv"))
        batch_id = payload.get("batch_id")
        skip_if_exists = payload.get("skip_if_exists", True)
        validation_threshold = payload.get("validation_threshold", 95.0)

        result = run_etl_pipeline(
            csv_file_path=csv_file_path,
            batch_id=batch_id,
            skip_if_exists=skip_if_exists,
            validation_threshold=validation_threshold
        )

        status_code = 200 if result.success else 207  # 207: multi-status / partial success semantics
        return JSONResponse(status_code=status_code, content={
            "status": "success" if result.success else "partial_or_failed",
            "summary": result.get_summary()
        })
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail="Failed to run ingestion")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.now().isoformat()}
    )
