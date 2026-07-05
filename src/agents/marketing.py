import json
import os
from src.tools.llm import call as llm_call
from src.tools.validator import validate_or_fail, load_schema
from src.tools.logger import info

_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "spec", "schema", "marketing_schema.json")


def run(insight_data: dict) -> dict:
    info("MarketingAgent", "Starting marketing generation")

    raw = llm_call("marketing", {"insight": insight_data})

    schema = load_schema(_SCHEMA_PATH)
    result = validate_or_fail(raw, schema)

    info("MarketingAgent", "Marketing generation complete",
         campaigns=len(result["campaign_suggestions"]),
         confidence=result["confidence_score"])

    return {"status": "success", "data": result}
