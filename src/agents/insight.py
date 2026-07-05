import json
import os
from src.tools.llm import call as llm_call
from src.tools.validator import validate_or_fail, load_schema
from src.tools.logger import info

_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "spec", "schema", "insight_schema.json")


def run(reviews: list[str], product_info: dict | None = None) -> dict:
    info("InsightAgent", "Starting insight analysis", review_count=len(reviews))

    raw = llm_call("insight", {"reviews": reviews, "product_info": product_info})

    schema = load_schema(_SCHEMA_PATH)
    result = validate_or_fail(raw, schema)

    info("InsightAgent", "Insight analysis complete",
         pain_points=len(result["pain_points"]),
         confidence=result["confidence_score"])

    return {"status": "success", "data": result}
