# Architecture Guide

## Overview

The system is a 3-agent pipeline orchestrated by a state machine. Each agent
has a single responsibility, communicates via validated JSON, and the pipeline
can retry upstream steps based on QA feedback.

The pipeline flow:

  User Input (reviews) --> Insight Agent --> Marketing Agent --> QA Agent --> Result

---

## Major Modules

### 1. Agents (src/agents/)

Each agent is a standalone function that takes structured input, calls the LLM,
validates the output against its schema, and returns the result.

**Customer Insight** (insight.py)
- Input: reviews list + product_info (optional)
- Output: pain_points, advantages, customer_segments, confidence_score
- Responsibility: Extract structured insights from raw reviews

**Marketing** (marketing.py)
- Input: insight data (pain points, advantages, segments)
- Output: campaign_suggestions, target_audience, key_messaging, confidence_score
- Responsibility: Generate marketing content from customer insights

**QA** (qa.py)
- Input: insight data + marketing data
- Output: overall_score, decision (APPROVED/REJECTED), issues, feedback
- Responsibility: Evaluate quality and decide approval status

Agents do not call each other directly. They are invoked by the workflow engine.

### 2. Workflow Engine (src/workflow/)

Three components:

- **state.py** -- 6-state enum: INIT, INSIGHT_DONE, MARKETING_DONE, QA_DONE,
  APPROVED, REJECTED
- **graph.py** -- defines allowed transitions between states
- **engine.py** -- orchestrator that runs the agents in sequence and manages
  the retry loop

The engine maintains:
- Current state
- Retry counter (max 3)
- Artifacts dict (insight, marketing, qa outputs)

Retry logic:
  QA_DONE --> APPROVED if score >= 80
          --> MARKETING_DONE if score < 80 and retries < 3
          --> REJECTED if score < 80 and retries >= 3

### 3. LLM Backend (src/tools/llm.py)

A single call(agent_type, data) function that dispatches to one of three
backends:

- **deepseek** -- calls DeepSeek API via OpenAI-compatible SDK
- **zhipuai** -- calls ZhipuAI API via OpenAI-compatible SDK
- **mock** -- keyword-based classification, zero dependencies

Each real backend sends a system prompt containing the agent's role and exact
JSON schema, then requests response_format=json_object. This ensures the LLM
returns valid parseable JSON.

If the API call fails, the system automatically falls back to mock mode.

### 4. Schema Validator (src/tools/validator.py)

A lightweight JSON Schema validator built without external libraries.

- Checks required fields exist
- Validates field types (string, number, array, object)
- Verifies enum values are valid
- Checks numeric ranges (min/max)
- Rejects extra fields (additionalProperties: false)

Each agent calls validate_or_fail() after receiving LLM output.

### 5. Configuration (src/config.py)

Loads settings from a .env file using manual parsing. Exposes:
- llm_backend: mock, deepseek, or zhipuai
- API keys and model names for each provider

### 6. Logger (src/tools/logger.py)

Outputs structured JSON lines to stdout with:
- timestamp, level, agent name, message, optional extra fields

### 7. UI Layer (app.py)

A Streamlit application that wraps the pipeline for interactive use.
Features: sidebar with sample data selector, text area for manual input,
real-time status updates, expandable result panels, execution info display.

The UI calls the same agent functions directly (not through the engine) to
enable per-step progress tracking. This reuses the same imports without
duplicating business logic.

---

## Data Flow

### End-to-End Trace

1. User provides reviews (CLI, file, or text area)
2. Engine receives reviews + product_info
3. Insight Agent calls llm.call("insight", data), validates result, stores it
4. Marketing Agent reads insight, calls llm.call("marketing", data), validates
5. QA Agent reads both, calls llm.call("qa", data), validates
6. If QA decision is APPROVED, pipeline ends with success
7. If REJECTED with retries remaining, re-run Marketing Agent (max 3 times)
8. Final state is APPROVED or REJECTED

### JSON Contract Example

Insight output -->
  pain_points: ["App crashes on startup"]
  advantages: ["Fast performance"]
  customer_segments: ["Power users"]
  confidence_score: 0.85

  (passed to Marketing Agent)

Marketing output -->
  campaign_suggestions: ["Campaign A"]
  target_audience: ["Power users"]
  key_messaging: ["Message 1"]
  confidence_score: 0.9

  (passed to QA Agent)

QA output -->
  overall_score: 92
  decision: "APPROVED"
  issues: []
  feedback: "Good alignment"

---

## Why This Architecture

### One Agent, One Responsibility

Each agent handles exactly one business task. This makes agents independently
testable and replaceable. Adding a new agent does not require modifying
existing ones.

### JSON-First Contracts

Agents communicate through predefined JSON schemas. This enforces structure,
enables automated validation, and makes debugging straightforward.

### State Machine Orchestration

Explicit states and transitions make the workflow predictable. The graph
enforces valid transitions and prevents invalid sequences.

### Retry Isolation

QA rejection only retriggers the Marketing Agent, not the Insight Agent. This
minimizes wasted LLM calls.

### Pluggable LLM Backend

The llm.py abstraction supports swapping between DeepSeek, ZhipuAI, or mock
mode with a single config change. Enables development without API keys.

### Minimal Dependencies

The core pipeline uses only Python standard library. External dependencies
are openai (for API calls) and streamlit (for UI).

---

## File Map

src/
  main.py              Entry point, CLI menu, --debug flag
  config.py            Loads .env, exposes settings
  agents/
    insight.py         run(reviews, product_info) -> insight JSON
    marketing.py       run(insight_data) -> marketing JSON
    qa.py              run(insight, marketing) -> qa JSON
  tools/
    llm.py             call(agent_type, data) -> JSON
    logger.py          structured JSON logging to stdout
    validator.py       validate(data, schema) -> errors list
  workflow/
    state.py           WorkflowState enum (6 states)
    graph.py           WorkflowGraph (transitions, routing)
    engine.py          WorkflowEngine (orchestrator + retry)
app.py                 Streamlit UI
tests/                 17 pytest tests
spec/schema/           3 JSON Schema files
