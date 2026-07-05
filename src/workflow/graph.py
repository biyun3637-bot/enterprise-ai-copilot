from src.workflow.state import WorkflowState


class WorkflowGraph:
    """Defines the state machine transitions for the 3-agent pipeline."""

    def __init__(self):
        self._edges: dict[WorkflowState, list[WorkflowState]] = {
            WorkflowState.INIT: [WorkflowState.INSIGHT_DONE],
            WorkflowState.INSIGHT_DONE: [WorkflowState.MARKETING_DONE],
            WorkflowState.MARKETING_DONE: [WorkflowState.QA_DONE],
            WorkflowState.QA_DONE: [WorkflowState.APPROVED, WorkflowState.REJECTED, WorkflowState.MARKETING_DONE],
        }

    def allowed_transitions(self, state: WorkflowState) -> list[WorkflowState]:
        return self._edges.get(state, [])

    def can_transition(self, current: WorkflowState, target: WorkflowState) -> bool:
        return target in self.allowed_transitions(current)

    def next_after_qa(self, decision: str, retry_count: int, max_retries: int) -> WorkflowState:
        if decision == "APPROVED":
            return WorkflowState.APPROVED
        if retry_count >= max_retries:
            return WorkflowState.REJECTED
        return WorkflowState.MARKETING_DONE
