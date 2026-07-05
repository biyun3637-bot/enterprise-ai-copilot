import json
import os
from src.tools.llm import call as llm_call
from src.tools.validator import validate_or_fail, load_schema
from src.tools.logger import info

_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "spec", "schema", "qa_schema.json")


def run(insight_data: dict, marketing_data: dict) -> dict:
    info("QAAgent", "Starting quality evaluation")

    raw = llm_call("qa", {"insight": insight_data, "marketing": marketing_data})

    schema = load_schema(_SCHEMA_PATH)
    result = validate_or_fail(raw, schema)

    info("QAAgent", "Quality evaluation complete",
         score=result["overall_score"],
         decision=result["decision"])

    return {"status": "success", "data": result}
