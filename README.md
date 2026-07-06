# Enterprise AI Growth Copilot

A lightweight multi-agent AI pipeline that analyzes customer reviews,
generates marketing content, and evaluates output quality.

---

## Business Problem

Enterprise teams spend significant time manually analyzing customer feedback,
crafting marketing messaging, and reviewing content quality. These repetitive
tasks are slow, inconsistent, and hard to scale across products and markets.

## Solution

A 3-agent pipeline that automates the workflow from raw reviews to approved
marketing output. Each agent communicates using strict JSON schemas. QA can
trigger up to 3 retries of the Marketing Agent if the score is below 80.

## Key Features

- 3 specialized agents with single responsibilities
- JSON-first contract between agents, validated against schemas
- State machine workflow with retry loop (max 3 retries)
- DeepSeek integration (falls back to mock if no API key)
- Structured logging at every step
- Streamlit UI for interactive use
- CLI menu for headless operation
- Debug mode with step-by-step trace
- 17 unit tests covering agents, workflow, and schemas
- Zero external dependencies for the core pipeline

## Technology Stack

- Language: Python 3.12
- LLM: DeepSeek (deepseek-chat) via OpenAI SDK
- UI: Streamlit
- Testing: pytest
- Schema validation: Custom validator (built-in)
- Config: .env file
- Logging: Structured JSON to stdout

## Project Structure

```
enterprise-ai-copilot/
  app.py                - Streamlit UI
  src/
    main.py             - CLI entry point
    config.py           - Config loader
    agents/
      insight.py        - Customer Insight Agent
      marketing.py      - Marketing Agent
      qa.py             - QA Evaluation Agent
    tools/
      llm.py            - LLM backend (DeepSeek / mock)
      logger.py         - Structured logging
      validator.py      - JSON Schema validation
    workflow/
      state.py          - State machine enum
      graph.py          - Transition rules
      engine.py         - Pipeline orchestrator
  spec/schema/          - JSON Schema files
  contracts/            - Agent contracts
  test_data/            - Sample review files
  tests/                - pytest test suite
  .env.example          - Config template
```

## How to Run

### Setup

```
git clone https://github.com/biyun3637-bot/enterprise-ai-copilot.git
cd enterprise-ai-copilot
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set LLM_BACKEND=deepseek and DEEPSEEK_API_KEY=sk-xxx
```

### CLI Mode

```
python -m src.main
python -m src.main --debug
```

### Streamlit UI

```
streamlit run app.py
```

### Tests

```
python -m pytest tests -v
```

All 17 tests pass.

## Demo

(Screenshots to be added)

Typical workflow:

1. Input 5+ product reviews
2. Insight Agent extracts pain points, advantages, segments
3. Marketing Agent generates campaign suggestions and key messages
4. QA Agent scores output, approves or triggers retry
5. Pipeline ends in APPROVED or REJECTED state

## Future Roadmap

- Result persistence to JSON/Markdown files
- More agents: report generation, pricing
- Web dashboard with history and comparison
- RAG integration for domain knowledge
- Multi-language review analysis
- CI/CD pipeline

---

*Production-style MVP. Designed for incremental extension without breaking
existing contracts.*
