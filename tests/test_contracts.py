import json
import os

# Schemas that agents must produce valid output for
_SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "spec", "schema")


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def test_insight_schema_is_valid():
    s = _load(os.path.join(_SCHEMA_DIR, "insight_schema.json"))
    assert s["type"] == "object"
    assert "pain_points" in s["required"]
    assert "advantages" in s["required"]
    assert "customer_segments" in s["required"]
    assert "confidence_score" in s["required"]


def test_marketing_schema_is_valid():
    s = _load(os.path.join(_SCHEMA_DIR, "marketing_schema.json"))
    assert s["type"] == "object"
    assert "campaign_suggestions" in s["required"]
    assert "target_audience" in s["required"]
    assert "key_messaging" in s["required"]
    assert "confidence_score" in s["required"]


def test_qa_schema_is_valid():
    s = _load(os.path.join(_SCHEMA_DIR, "qa_schema.json"))
    assert s["type"] == "object"
    assert "overall_score" in s["required"]
    assert "decision" in s["required"]
    assert s["properties"]["decision"]["enum"] == ["APPROVED", "REJECTED"]
    assert s["properties"]["overall_score"]["minimum"] == 0
    assert s["properties"]["overall_score"]["maximum"] == 100


def test_all_schemas_allow_no_extra_fields():
    for name in ("insight_schema.json", "marketing_schema.json", "qa_schema.json"):
        s = _load(os.path.join(_SCHEMA_DIR, name))
        assert s.get("additionalProperties") is False, f"{name} must forbid extra fields"
