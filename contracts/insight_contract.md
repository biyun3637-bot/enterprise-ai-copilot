# Insight Contract

## Input Schema
```json
{
  "reviews": "array<string>",
  "product_info": "object | null"
}

## Output Schema
Must match `insight_schema.json`

## Hard Rules
-MUST return JSON only
-MUST include all required fields
-MUST NOT include free text

## Failure Mode
{
  "status": "insufficient_data",
  "reason": "string"
}