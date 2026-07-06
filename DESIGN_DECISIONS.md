# Design Decisions

## Multi-Agent Architecture

The system decomposes a complex business workflow into three specialized agents. Each agent handles exactly one transformation step: raw data to insight, insight to marketing, and output to evaluation. This decomposition makes the system modular, testable, and extensible.

A monolithic design would couple analysis, generation, and evaluation into a single prompt, making it harder to debug, swap components, or add new capabilities without regression.

## Single Responsibility Principle

Each agent has one clear responsibility and does not cross into another agent's domain:

- Insight Agent identifies customer needs but does not write marketing copy.
- Marketing Agent generates content but does not analyze reviews.
- QA Agent evaluates quality but does not modify upstream output.

This separation means each agent can be developed, tested, and replaced independently. A change to the marketing strategy does not require changing the insight logic.

## JSON-First Communication

Agents communicate exclusively through structured JSON. Free text is not allowed between agents. This decision provides several benefits:

1. **Schema enforcement** -- every message has a contract, validated at runtime.
2. **Debugging clarity** -- each step's output is inspectable and comparable.
3. **Language independence** -- agents could be implemented in different languages.
4. **Testability** -- validation logic is separate from generation logic.

The alternative (natural language between agents) would introduce ambiguity, make validation harder, and increase the risk of hallucination propagation.

## Contracts

Each agent has a published contract (spec/schema/) that defines exactly what it expects and produces. These contracts serve as:

1. **Boundaries** -- clear interface between components.
2. **Documentation** -- a developer can understand data flow without reading implementation code.
3. **Test fixtures** -- schema files are used directly in test assertions.

Contracts are versioned in the agent registry (spec/agent_registry.json) and are immutable within a version. Any breaking change requires a version bump.

## Workflow Orchestration

The workflow is modeled as a state machine rather than a sequential script. This provides:

1. **Predictable transitions** -- each state knows its valid next states.
2. **Safety** -- invalid transitions are rejected at runtime.
3. **Observability** -- current state is always known and logged.
4. **Retry management** -- retry logic is a property of the state graph, not scattered in if/else blocks.

A state machine is more complex than a simple script but scales better as workflows grow. Adding a new agent means adding a new state and its transitions without touching other states.

## QA Agent

The QA Agent acts as a quality gate between generation and consumption. It prevents low-quality marketing content from reaching the output stage. Key design choices:

1. **Score threshold** -- 80/100 is the approval boundary, simple and auditable.
2. **Retry isolation** -- only the Marketing Agent is retried, not Insight. This assumes the insight analysis is correct and the marketing generation needs adjustment.
3. **Max retries** -- 3 attempts prevent infinite loops while allowing multiple chances for improvement.

The alternative (no QA or human-only review) would either allow low-quality output or create a bottleneck. Automated QA with retry is a pragmatic middle ground.

## Schema Validation

Validation is implemented as a standalone tool (src/tools/validator.py) rather than embedded in each agent. This keeps agents focused on their primary task and makes the validation logic reusable.

The custom validator was chosen over a library (jsonschema) to:

1. Avoid external dependencies for core functionality.
2. Keep error messages simple and actionable.
3. Make validation logic auditable in a single file.

The validator checks required fields, types, enums, numeric ranges, and rejects unexpected fields. This catches most common LLM output errors before they propagate.

## Logging

All agent activity is logged as structured JSON to stdout. This format was chosen over plain text because:

1. JSON is parseable by log aggregators (ELK, Datadog, etc.).
2. Each log entry carries metadata (agent name, processing time, confidence score).
3. Structured logs can be filtered, searched, and analyzed programmatically.

The logger is a simple module (src/tools/logger.py) with no external dependencies. It supports levels (DEBUG, INFO, WARN, ERROR) and optional extra fields.

## Streamlit as Presentation Layer

Streamlit was chosen as the UI layer for pragmatic reasons:

1. **Python-native** -- no separate frontend language or framework.
2. **Stateful widgets** -- session state persists across interactions.
3. **Rapid development** -- single-file app with minimal boilerplate.
4. **Data display** -- built-in components for JSON, metrics, expanders, and status indicators.

The UI calls the same agent functions as the CLI, ensuring consistent behavior. The Streamlit layer is purely a presentation wrapper with no business logic. A different frontend (REST API, CLI, batch processing) can be added without modifying the agents.