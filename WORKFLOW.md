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

---

## Shared Context (Business Brief V2)

Starting from V2, the pipeline carries a **Business Brief** as shared
read-only context across all agents.

### Flow

```
Pipeline Start
    |
    +-- Load Business Brief from input
    |
    v
Business Brief (immutable throughout run)
    |          |          |
    v          v          v
Insight --> Marketing --> QA
```

### Rules

- Business Brief is loaded once at the beginning of each run.
- It is **not a pipeline node** and does not have its own state.
- It is available as a read-only dict to every agent.
- Agents cannot modify the Business Brief.
- If the Business Brief is invalid, the pipeline should reject it
  before entering the first agent.

### Rationale

In V1, product information was passed only to the Insight Agent as an
optional parameter. Marketing and QA had no direct access to business
context. In V2, all agents receive the same Business Brief, ensuring
consistent business logic across the entire pipeline.
