from enum import Enum


class WorkflowState(str, Enum):
    INIT = "INIT"
    INSIGHT_DONE = "INSIGHT_DONE"
    MARKETING_DONE = "MARKETING_DONE"
    QA_DONE = "QA_DONE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

    def is_final(self) -> bool:
        return self in (WorkflowState.APPROVED, WorkflowState.REJECTED)

    def __str__(self) -> str:
        return self.value
