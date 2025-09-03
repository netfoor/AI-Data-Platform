"""
Natural Language Query (NLQ) module to map questions to SQL queries.
Simple rule-based implementation that leverages SQLQueryInterface.
"""
import logging
from datetime import date
from typing import Dict, Any, Optional

from .sql_queries import sql_interface, QueryResult

logger = logging.getLogger(__name__)


def _parse_dates(payload: Dict[str, Any]) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    # Accept ISO strings or date objects; let DB layer handle dates
    if payload.get("start_date"):
        params["start_date"] = payload["start_date"]
    if payload.get("end_date"):
        params["end_date"] = payload["end_date"]
    if payload.get("previous_start_date"):
        params["previous_start_date"] = payload["previous_start_date"]
    if payload.get("previous_end_date"):
        params["previous_end_date"] = payload["previous_end_date"]
    return params


def map_question_to_query(question: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Map a natural language question to a predefined SQL query and parameters.
    Returns dict with keys: query_name, parameters
    """
    if payload is None:
        payload = {}

    q = (question or "").lower()
    params = _parse_dates(payload)

    # Period comparison intent
    if "compare" in q and ("last 30" in q or "prior" in q or "previous" in q):
        # Expect four dates optionally; otherwise caller should supply
        return {"query_name": "period_comparison", "parameters": params}

    # Platform performance intent
    if "platform" in q or "by platform" in q:
        return {"query_name": "platform_performance", "parameters": params}

    # Campaign analysis intent
    if "campaign" in q:
        return {"query_name": "campaign_analysis", "parameters": params}

    # Trend intent
    if "trend" in q or "daily" in q:
        return {"query_name": "trend_analysis", "parameters": params}

    # Default: daily metrics
    return {"query_name": "daily_metrics", "parameters": params}


def execute_nlq(question: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute an NLQ by mapping to a query and running it via SQLQueryInterface.
    Returns structured response with data and a simple summary.
    """
    mapping = map_question_to_query(question, payload)
    query_name = mapping["query_name"]
    parameters = mapping["parameters"]

    result: QueryResult = sql_interface.execute_predefined_query(query_name, parameters)

    formatted_summary = sql_interface.format_query_result(result, format_type="summary")

    return {
        "query_name": query_name,
        "parameters": parameters,
        "success": result.success,
        "data": result.data,
        "row_count": result.row_count,
        "execution_time": result.execution_time,
        "summary": formatted_summary,
        "error": result.error_message,
    }


