# Workflow Specification

## States

The pipeline uses a 6-state finite state machine:

INIT -- pipeline created, ready to start
INSIGHT_DONE -- Insight Agent completed
MARKETING_DONE -- Marketing Agent completed
QA_DONE -- QA Agent completed
APPROVED -- final, successful
REJECTED -- final, failed after max retries

States are defined as a Python StrEnum in src/workflow/state.py.

## Execution Order

### Normal Flow

INIT to INSIGHT_DONE to MARKETING_DONE to QA_DONE to APPROVED

Each transition requires the agent to complete successfully with valid JSON.

### Retry Flow

If QA score is below 80, the engine re-runs Marketing Agent (up to 3 times).

## Retry Logic

- Score >= 80: APPROVED
- Score < 80 and retries < 3: retry Marketing
- Score < 80 and retries >= 3: REJECTED

Only Marketing is retried, not Insight. This avoids re-analyzing reviews.

## Final States

APPROVED -- QA score >= 80 at any attempt
REJECTED -- QA score < 80 after 3 retries

Both are terminal. Pipeline stops when either is reached.

## Error Handling

API call fails: logs error, falls back to mock mode, continues
Invalid JSON: raises exception, caught by call()
Schema validation fails: raises ValueError with field details
Invalid state transition: raises RuntimeError
Empty reviews: shows warning, stops

The schema validator checks required fields, types, enums, ranges, and forbids extra fields.

## Source Files

State enum: src/workflow/state.py
Transitions: src/workflow/graph.py
Orchestration: src/workflow/engine.py
