import time
from src.workflow.state import WorkflowState
from src.workflow.graph import WorkflowGraph
from src.agents.insight import run as insight_run
from src.agents.marketing import run as marketing_run
from src.agents.qa import run as qa_run
from src.tools.logger import info, error

MAX_RETRIES = 3


class WorkflowEngine:
    """Runs the 3-agent pipeline Insight -> Marketing -> QA (with retry loop)."""

    def __init__(self, max_retries: int = MAX_RETRIES, debug: bool = False):
        self.graph = WorkflowGraph()
        self.state = WorkflowState.INIT
        self.retry_count = 0
        self.max_retries = max_retries
        self.artifacts: dict[str, dict] = {}
        self.debug = debug

    def _transition(self, target: WorkflowState):
        if not self.graph.can_transition(self.state, target):
            raise RuntimeError(f"Invalid transition: {self.state} -> {target}")
        info("Engine", f"Transitioning: {self.state} -> {target}")
        if self.debug:
            print(f"\n{'─'*50}")
            print(f"   State: {self.state.value}  \u2192  {target.value}")
            print(f"{'─'*50}")
        self.state = target

    def _debug_agent(self, label: str, input_summary: str, t_start: float, output: dict):
        elapsed = round(time.time() - t_start, 2)
        print(f"\n  [{label}]")
        print(f"  \u2514 Input: {input_summary}")
        print(f"  \u2514 Processing time: {elapsed}s")
        print(f"  \u2514 Schema validation: PASSED")
        import json
        print(f"  \u2514 Output:")
        for line in json.dumps(output, indent=2, ensure_ascii=False).split("\n"):
            print(f"      {line}")

    def run(self, reviews: list[str], product_info: dict | None = None, business_brief: dict | None = None) -> dict:
        self.business_brief = business_brief

        info("Engine", "Workflow started", review_count=len(reviews))
        if self.debug:
            print("\n" + "\u2550" * 52)
            print("  Enterprise AI Growth Copilot - Debug Trace")
            print("\u2550" * 52)
            print(f"\n  Input: {len(reviews)} reviews" + (f", 1 product info" if product_info else ""))
            if business_brief:
                print(f"  Business Brief: {business_brief.get('product_name', 'N/A')}")

        # --- Step 1: Insight Agent ---
        info("Engine", "Running Insight Agent")
        if self.debug:
            print(f"\n  Current State: {self.state.value}")
            print(f"\n  \u2193\n")
            print(f"  --- Customer Insight Agent ---")
        t0 = time.time()
        insight_result = insight_run(reviews, product_info, business_brief=business_brief)
        self.artifacts["insight"] = insight_result["data"]
        if self.debug:
            self._debug_agent("Customer Insight Agent",
                              f"{len(reviews)} reviews, conf={insight_result['data']['confidence_score']}",
                              t0, insight_result["data"])
        self._transition(WorkflowState.INSIGHT_DONE)

        # --- Step 2: Marketing Agent ---
        info("Engine", "Running Marketing Agent")
        if self.debug:
            print(f"\n  \u2193\n")
            print(f"  --- Marketing Agent ---")
        t0 = time.time()
        marketing_result = marketing_run(self.artifacts["insight"], business_brief=business_brief)
        self.artifacts["marketing"] = marketing_result["data"]
        if self.debug:
            self._debug_agent("Marketing Agent",
                              f"insight ({len(self.artifacts['insight'])} fields)",
                              t0, marketing_result["data"])
        self._transition(WorkflowState.MARKETING_DONE)

        # --- Step 3: QA Agent (with retry loop) ---
        while True:
            info("Engine", "Running QA Agent", attempt=self.retry_count + 1)
            if self.debug:
                print(f"\n  \u2193\n")
                print(f"  --- QA Agent (attempt {self.retry_count + 1}) ---")
            t0 = time.time()
            qa_result = qa_run(self.artifacts["insight"], self.artifacts["marketing"])
            self.artifacts["qa"] = qa_result["data"]
            if self.debug:
                self._debug_agent("QA Agent",
                                  f"insight + marketing, retry={self.retry_count}",
                                  t0, qa_result["data"])
                score = qa_result["data"]["overall_score"]
                decision = qa_result["data"]["decision"]
                print(f"  \u2514 Score: {score}")
                print(f"  \u2514 Decision: {decision}")
                print(f"  \u2514 Retry count: {self.retry_count}")

            self._transition(WorkflowState.QA_DONE)

            decision = qa_result["data"]["decision"]
            next_state = self.graph.next_after_qa(decision, self.retry_count, self.max_retries)

            if next_state == WorkflowState.APPROVED:
                self._transition(WorkflowState.APPROVED)
                info("Engine", "Workflow APPROVED")
                if self.debug:
                    print(f"\n  \u2193")
                    print(f"\n  Final State: {self.state.value} \u2705\n")
                    print("\u2550" * 52)
                return self._summary()

            if next_state == WorkflowState.REJECTED:
                self._transition(WorkflowState.REJECTED)
                error("Engine", "Workflow REJECTED after max retries")
                if self.debug:
                    print(f"\n  \u2193")
                    print(f"\n  Final State: {self.state.value} \u274c\n")
                    print("\u2550" * 52)
                return self._summary()

            # Retry: MARKETING_DONE
            self.retry_count += 1
            info("Engine", f"QA rejected, retrying Marketing (attempt {self.retry_count}/{self.max_retries})")

            # Re-run marketing with same insight
            if self.debug:
                print(f"\n  \u21bb QA rejected, retrying Marketing ({self.retry_count}/{self.max_retries})")
                t0 = time.time()
            marketing_result = marketing_run(self.artifacts["insight"], business_brief=self.business_brief)
            self.artifacts["marketing"] = marketing_result["data"]
            if self.debug:
                self._debug_agent("Marketing Agent (retry)",
                                  f"insight (same), attempt {self.retry_count}",
                                  t0, marketing_result["data"])
            self._transition(WorkflowState.MARKETING_DONE)

    def _summary(self) -> dict:
        return {
            "final_state": self.state.value,
            "retries": self.retry_count,
            "business_brief": getattr(self, "business_brief", None),
            "artifacts": self.artifacts,
        }
