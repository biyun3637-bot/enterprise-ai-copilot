from src.agents.insight import run as insight_run
from src.tools.validator import load_schema, validate
import os

_SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "spec", "schema")


def test_insight_returns_valid_json():
    reviews = ["The product is too expensive", "Great build quality"]
    result = insight_run(reviews, {"name": "Test Widget", "version": "1.0"})

    assert result["status"] == "success"
    data = result["data"]
    assert "pain_points" in data
    assert "advantages" in data
    assert "customer_segments" in data
    assert "confidence_score" in data


def test_insight_output_matches_schema():
    schema = load_schema(os.path.join(_SCHEMA_DIR, "insight_schema.json"))
    reviews = ["Battery drains fast", "Easy to set up and use"]
    result = insight_run(reviews, None)
    errors = validate(result["data"], schema)
    assert not errors, f"Schema validation failed: {errors}"


def test_insight_with_empty_reviews():
    result = insight_run([], None)
    assert result["status"] == "success"
    assert len(result["data"]["pain_points"]) > 0
    assert len(result["data"]["advantages"]) > 0


def test_insight_confidence_in_range():
    result = insight_run(["Great product", "Works well"], None)
    score = result["data"]["confidence_score"]
    assert 0.0 <= score <= 1.0
