# Business Brief

## Purpose

Business Brief provides shared business context for all AI agents.

Instead of asking every agent to infer product information from reviews,
the system supplies standardized business information.

This improves consistency and reduces hallucination.

---

## Shared Context

### Product

- Product Name
- Category
- Brand
- SKU

### Market

- Target Market
- Language
- Currency

### Customer

- Target Audience
- Customer Persona

### Business

- Brand Position
- Price Range
- Business Goal

### Product Features

- Core Features
- Selling Points
- Unique Advantages

---

## Design Principle

Business Brief is shared by all agents.

Business Brief is NOT an Agent.

Business Brief is immutable during one workflow execution.