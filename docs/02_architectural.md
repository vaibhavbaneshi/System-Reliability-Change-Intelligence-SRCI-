# System Architecture

SRCI is designed as an event-driven, read-only intelligence platform composed of four major layers.

---

## High-Level Components

1. Ingestion Layer
2. Knowledge & Graph Layer
3. Intelligence & Reasoning Layer
4. Presentation Layer (Dashboard)

---

## 1. Ingestion Layer

Responsible for collecting metadata and signals from external systems.

### Responsibilities
- Clone and read Git repositories (read-only)
- Parse code structure and dependencies
- Ingest schema metadata
- Load structured logs, metrics, and traces (time-bounded)

### Key Properties
- Event-driven (PR opened, change submitted, incident registered)
- No continuous live scanning
- Least-privilege access

---

## 2. Knowledge & Graph Layer

Acts as the system of record for SRCI.

### Stores
- Services, APIs, databases
- Dependencies and relationships
- Changes and incidents
- Historical evidence

### Characteristics
- Graph-first data model
- Time-aware (everything is versioned)
- Immutable historical records

---

## 3. Intelligence & Reasoning Layer

Produces insights using deterministic analysis combined with AI reasoning.

### Capabilities
- Change impact traversal
- Incident causal graph construction
- Root cause hypothesis ranking
- Confidence scoring

### AI Usage
- Selective and constrained
- Used for explanation and comparison
- Never used for discovery of structure

---

## 4. Presentation Layer

Exposes SRCI intelligence via a web dashboard.

### Goals
- Visualize system structure
- Explain impact and causality
- Enable fast human decision-making

---

## Design Principles

- Explainability over automation
- Graph reasoning over flat analysis
- Event-driven over continuous scanning
- Trust and auditability over AI novelty