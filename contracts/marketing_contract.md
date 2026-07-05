```markdown id="t5"
# Marketing Contract

## Input
- insight_json (required)

## Output
Must match `marketing_schema.json`

## Rules
- Cannot modify insight data
- Only extend with marketing layer
- Must be JSON only

## Failure Mode
```json
{
  "status": "invalid_insight",
  "reason": "string"
}