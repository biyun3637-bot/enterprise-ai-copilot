```markdown id="t7"
# Workflow State Machine

## States
- INIT
- INSIGHT_DONE
- MARKETING_DONE
- QA_DONE
- APPROVED
- REJECTED

## Transitions

INIT → INSIGHT_DONE
- when Insight output is valid JSON

INSIGHT_DONE → MARKETING_DONE
- when Marketing receives Insight JSON

MARKETING_DONE → QA_DONE
- when Marketing output valid

QA_DONE → APPROVED
- if score >= 80

QA_DONE → MARKETING_DONE
- if score < 80 (retry loop)

QA_DONE → REJECTED
- if repeated failure > 3