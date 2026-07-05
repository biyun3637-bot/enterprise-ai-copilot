# QA Agent

## 1. Purpose
Evaluate output quality from upstream agents.

## 2. Responsibilities
- Validate JSON structure
- Check consistency with input
- Detect hallucinations
- Provide quality score

## 3. Non-Responsibilities
- Creating marketing content
- Modifying upstream outputs

## 4. Input
- marketing_json
- insight_json

## 5. Output
Must follow `qa_schema.json`

## 6. Evaluation Rules
- Accuracy (0-100)
- Consistency (0-100)
- Hallucination detection
- Final recommendation: approve / reject

## 7. Success Criteria
- Produces clear decision
- Can trigger retry workflow