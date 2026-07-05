from src.workflow.state import WorkflowState
from src.workflow.graph import WorkflowGraph
from src.agents.insight import run as insight_run
from src.agents.marketing import run as marketing_run
from src.agents.qa import run as qa_run
from src.tools.logger import info, error

MAX_RETRIES = 3


class WorkflowEngine:
    """Runs the 3-agent pipeline Insight -> Marketing -> QA (with retry loop)."""

    def __init__(self, max_retries: int = MAX_RETRIES):
        self.graph = WorkflowGraph()
        self.state = WorkflowState.INIT
        self.retry_count = 0
        self.max_retries = max_retries
        self.artifacts: dict[str, dict] = {}

    def _transition(self, target: WorkflowState):
        if not self.graph.can_transition(self.state, target):
            raise RuntimeError(f"Invalid transition: {self.state} -> {target}")
        info("Engine", f"Transitioning: {self.state} -> {target}")
        self.state = target

    def run(self, reviews: list[str], product_info: dict | None = None) -> dict:
        info("Engine", "Workflow started", review_count=len(reviews))

        # --- Step 1: Insight Agent ---
        info("Engine", "Running Insight Agent")
        insight_result = insight_run(reviews, product_info)
        self.artifacts["insight"] = insight_result["data"]
        self._transition(WorkflowState.INSIGHT_DONE)

        # --- Step 2: Marketing Agent ---
        info("Engine", "Running Marketing Agent")
        marketing_result = marketing_run(self.artifacts["insight"])
        self.artifacts["marketing"] = marketing_result["data"]
        self._transition(WorkflowState.MARKETING_DONE)

        # --- Step 3: QA Agent (with retry loop) ---
        while True:
            info("Engine", "Running QA Agent", attempt=self.retry_count + 1)
            qa_result = qa_run(self.artifacts["insight"], self.artifacts["marketing"])
            self.artifacts["qa"] = qa_result["data"]

            self._transition(WorkflowState.QA_DONE)

            decision = qa_result["data"]["decision"]
            next_state = self.graph.next_after_qa(decision, self.retry_count, self.max_retries)

            if next_state == WorkflowState.APPROVED:
                self._transition(WorkflowState.APPROVED)
                info("Engine", "Workflow APPROVED")
                return self._summary()

            if next_state == WorkflowState.REJECTED:
                self._transition(WorkflowState.REJECTED)
                error("Engine", "Workflow REJECTED after max retries")
                return self._summary()

            # Retry: MARKETING_DONE
            self.retry_count += 1
            info("Engine", f"QA rejected, retrying Marketing (attempt {self.retry_count}/{self.max_retries})")

            # Re-run marketing with same insight
            marketing_result = marketing_run(self.artifacts["insight"])
            self.artifacts["marketing"] = marketing_result["data"]
            self._transition(WorkflowState.MARKETING_DONE)

    def _summary(self) -> dict:
        return {
            "final_state": self.state.value,
            "retries": self.retry_count,
            "artifacts": self.artifacts,
        }
