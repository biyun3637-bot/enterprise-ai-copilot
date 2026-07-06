# Interview Guide

## 30-Second Introduction

I built a multi-agent AI system that automates customer feedback analysis
and marketing content generation. Three specialized agents work in sequence:
Insight extracts pain points from reviews, Marketing generates campaigns,
and QA evaluates quality with automatic retry. The system runs with DeepSeek
and is fully testable end-to-end.

---

## 3-Minute Project Introduction

### The Problem

Enterprise teams spend significant time manually reviewing customer feedback,
writing marketing copy, and checking content quality. This process is slow,
inconsistent, and does not scale across products.

### The Solution

A 3-agent pipeline that turns raw reviews into approved marketing output.

- Customer Insight Agent identifies pain points, advantages, and segments
- Marketing Agent generates campaign suggestions and key messages
- QA Agent scores quality and approves or rejects, with up to 3 retries

Each agent outputs validated JSON and communicates through strict contracts.
The workflow is orchestrated by a state machine with logging at every step.

### Key Result

The system runs end-to-end with a single command. It supports CLI and
Streamlit UI, works with or without an API key (mock fallback), and passes
17 unit tests.

---

## Business Value

### For AI Operations

- Reduce manual work by automating feedback analysis
- Standardize quality through automated QA gating
- Audit every step with structured JSON logging
- Control costs with mock mode for development

### For AI Solutions

- Pluggable LLM backend: swap between DeepSeek, ZhipuAI, or mock
- JSON contracts: agents communicate through versioned schemas
- Minimal dependencies: core pipeline uses only Python standard library

### For AI Products

- Extensible architecture: add new agents without modifying existing code
- Dual interface: CLI for automation, Streamlit for interactive use
- Retry isolation: QA only retriggers Marketing, minimizing wasted calls

---

## Technical Highlights

### 1. State Machine Orchestration

6-state FSM with explicit transition graph. Retry logic is a routing
decision from QA_DONE based on score and retry count.

### 2. JSON-First Agent Communication

All agents exchange structured JSON validated against published schemas.
Custom validator checks types, enums, ranges, and forbids extra fields.

### 3. Pluggable LLM Abstraction

Single call() dispatches to DeepSeek, ZhipuAI, or mock. System prompts
include exact JSON schema with structured output mode. On API failure,
falls back to mock mode transparently.

### 4. Retry Isolation

QA rejection only retriggers Marketing, not Insight. Saves cost and
time compared to re-analyzing reviews.

### 5. Streamlit UI Without Backend Changes

UI calls the same agent functions as the CLI, not through the engine.
Enables per-step progress without modifying workflow code.

---

## Challenges

### 1. Mock LLM Realism

Keyword-based mock made obvious classification errors. Fixed by expanding
keyword coverage, but a mock cannot match LLM reasoning quality.
Lesson: Use real LLM for logic validation, mock only for pipeline testing.

### 2. Abstraction vs. Dependency Weight

OpenAI SDK introduced heavy dependencies for what is a single API call.
For a zero-dependency core, raw HTTP might be cleaner.
Lesson: Match dependency weight to actual usage patterns.

### 3. Streamlit Widget Lifecycle

Text area ignores value parameter when session state key exists. Sample
data selector failed silently until direct key manipulation was used.
Lesson: Use st.session_state.key directly, not value parameter.

### 4. Sandbox Development

Restricted network and filesystem access required working through sandbox
tools for all file operations. Package installs needed escalated permissions.
Lesson: Develop locally first, then adapt for restricted environments.

---

## Lessons Learned

### Architecture

- Start with mock mode, add real LLM later
- Use strict schemas (additionalProperties: false)
- State machines simplify retry logic

### Implementation

- Test mock outputs against real data early
- Use session state keys directly in Streamlit
- Minimize dependencies for easier onboarding

### Process

- Define success criteria before coding
- Isolate environment-specific workarounds
- Document decisions as they happen
