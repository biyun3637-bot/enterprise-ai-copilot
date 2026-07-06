import json
import os
from src.tools.llm import call as llm_call
from src.tools.validator import validate_or_fail, load_schema
from src.tools.logger import info

_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "spec", "schema", "qa_schema.json")


def run(insight_data: dict, marketing_data: dict, business_brief: dict | None = None) -> dict:
    info("QAAgent", "Starting quality evaluation")

    data = {"insight": insight_data, "marketing": marketing_data}
    if business_brief:
        data["business_brief"] = business_brief
        info("QAAgent", "Business Brief received")
    raw = llm_call("qa", data)

    schema = load_schema(_SCHEMA_PATH)
    result = validate_or_fail(raw, schema)

    info("QAAgent", "Quality evaluation complete",
         score=result["overall_score"],
         decision=result["decision"])

    return {"status": "success", "data": result}
