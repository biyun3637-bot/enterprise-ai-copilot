```markdown id="t6"
# QA Contract

## Input
- insight_json
- marketing_json

## Output
Must match `qa_schema.json`

## Responsibilities
- Validate correctness
- Score quality
- Decide approval

## Output Decision
- approve
- reject

## Failure Mode
```json
{
  "status": "evaluation_failed",
  "reason": "string"
}