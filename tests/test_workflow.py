from src.workflow.state import WorkflowState
from src.workflow.graph import WorkflowGraph
from src.workflow.engine import WorkflowEngine
from src.tools.logger import set_level


def test_state_enum_values():
    assert WorkflowState.INIT.value == "INIT"
    assert WorkflowState.APPROVED.value == "APPROVED"
    assert WorkflowState.REJECTED.value == "REJECTED"


def test_final_states():
    assert WorkflowState.APPROVED.is_final()
    assert WorkflowState.REJECTED.is_final()
    assert not WorkflowState.INIT.is_final()


def test_graph_allowed_transitions():
    g = WorkflowGraph()
    assert WorkflowState.INSIGHT_DONE in g.allowed_transitions(WorkflowState.INIT)
    assert WorkflowState.MARKETING_DONE in g.allowed_transitions(WorkflowState.INSIGHT_DONE)
    assert WorkflowState.QA_DONE in g.allowed_transitions(WorkflowState.MARKETING_DONE)
    qa_next = g.allowed_transitions(WorkflowState.QA_DONE)
    assert WorkflowState.APPROVED in qa_next
    assert WorkflowState.REJECTED in qa_next
    assert WorkflowState.MARKETING_DONE in qa_next


def test_graph_next_after_qa():
    g = WorkflowGraph()
    assert g.next_after_qa("APPROVED", 0, 3) == WorkflowState.APPROVED
    assert g.next_after_qa("REJECTED", 0, 3) == WorkflowState.MARKETING_DONE
    assert g.next_after_qa("REJECTED", 3, 3) == WorkflowState.REJECTED
    assert g.next_after_qa("REJECTED", 4, 3) == WorkflowState.REJECTED


def test_workflow_engine_runs_end_to_end():
    set_level("ERROR")
    reviews = ["UI is confusing", "Fast performance"]
    engine = WorkflowEngine(max_retries=3)
    result = engine.run(reviews, {"name": "Test"})

    assert result["final_state"] in ("APPROVED", "REJECTED")
    assert "insight" in result["artifacts"]
    assert "marketing" in result["artifacts"]
    assert "qa" in result["artifacts"]


def test_workflow_insight_has_required_fields():
    set_level("ERROR")
    reviews = ["Buggy software", "Good value"]
    engine = WorkflowEngine(max_retries=3)
    result = engine.run(reviews, None)

    insight = result["artifacts"]["insight"]
    assert "pain_points" in insight
    assert "advantages" in insight
    assert "customer_segments" in insight
    assert "confidence_score" in insight


def test_workflow_marketing_has_required_fields():
    set_level("ERROR")
    reviews = ["Great tool", "Needs better docs"]
    engine = WorkflowEngine(max_retries=3)
    result = engine.run(reviews, None)

    marketing = result["artifacts"]["marketing"]
    assert "campaign_suggestions" in marketing
    assert "target_audience" in marketing
    assert "key_messaging" in marketing
    assert "confidence_score" in marketing


def test_workflow_qa_has_required_fields():
    set_level("ERROR")
    reviews = ["Average product", "Okay support"]
    engine = WorkflowEngine(max_retries=3)
    result = engine.run(reviews, None)

    qa = result["artifacts"]["qa"]
    assert "overall_score" in qa
    assert "decision" in qa
    assert "issues" in qa
    assert "feedback" in qa
    assert qa["decision"] in ("APPROVED", "REJECTED")


def test_workflow_debug_mode_does_not_crash():
    set_level("ERROR")
    reviews = ["Great product", "Terrible support"]
    engine = WorkflowEngine(max_retries=3, debug=True)
    result = engine.run(reviews, None)
    assert result["final_state"] in ("APPROVED", "REJECTED")
    assert "insight" in result["artifacts"]
    assert "marketing" in result["artifacts"]
    assert "qa" in result["artifacts"]
