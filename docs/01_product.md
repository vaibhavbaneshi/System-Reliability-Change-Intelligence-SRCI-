# PRODUCT.md  
## SRCI – System Reliability & Change Intelligence

---

## 1. Problem Statement

Modern engineering organizations face two tightly coupled problems:

### 1. Change Blindness (Pre-Production)
Engineers make code, schema, or configuration changes without clear visibility into downstream impact. This leads to:
- Unexpected service failures
- Repeated incidents
- Reactive firefighting

### 2. Incident Opacity (Post-Production)
When incidents occur:
- Logs, metrics, and traces are fragmented
- Root cause analysis is manual and slow
- Teams rely on intuition and tribal knowledge

Existing tools focus on observability or CI checks, but none provide **end-to-end intelligence connecting changes to failures**.

---

## 2. Product Vision

SRCI is an AI-powered engineering intelligence platform that:

- Predicts what can break **before a change is deployed**
- Automatically investigates **why production broke**
- Learns continuously from historical incidents
- Produces **evidence-based, explainable outputs**, not black-box answers

SRCI acts as a **reliability co-pilot** for SREs and platform engineers.

---

## 3. Target Users

### Primary Users
- Site Reliability Engineers (SREs)
- Platform / Backend Engineers

### Secondary Users
- Engineering Managers
- DevOps / Infrastructure teams

---

## 4. Core User Flows (MVP)

### Flow 1: Change Impact Analysis (Pre-Deployment)

**User Story**  
As an engineer, I want to understand the potential impact of a proposed change before deploying it.

**Flow**
1. User submits a change (PR, diff, schema update, config change)
2. SRCI analyzes the change against the system dependency graph
3. SRCI evaluates risk using:
   - Dependency depth and blast radius
   - Historical incidents
   - Component criticality
4. SRCI outputs:
   - Affected services and components
   - Risk score
   - AI-generated explanation
   - Supporting evidence

---

### Flow 2: Incident Investigation (Post-Failure)

**User Story**  
As an SRE, I want the system to analyze an incident and propose a likely root cause with evidence.

**Flow**
1. Incident is registered (manual or via alert)
2. SRCI ingests logs, metrics, and traces for the incident window
3. Signals are correlated by time and dependency
4. SRCI builds a causal incident graph
5. SRCI outputs:
   - Ranked root-cause hypotheses
   - Evidence chain
   - Confidence score

---

## 5. Key Differentiators

- Dependency and causality graphs as first-class entities
- Unified pre-deployment and post-incident intelligence
- Explainable AI reasoning grounded in system structure
- Learning loop from incidents back into future change predictions

SRCI is a **platform**, not a chatbot.

---

## 6. Inputs

SRCI operates on **read-only, metadata-level inputs**:

### Allowed Inputs
- Git repositories (read-only)
- Git diffs / pull requests
- Database schemas (metadata only)
- Structured logs
- Aggregated metrics
- Trace summaries

### Explicitly Disallowed Inputs
- Live production data rows
- Secrets or credentials
- User PII
- Free-form conversational input

---

## 7. Outputs

SRCI produces **structured intelligence artifacts**, not raw answers:

- System dependency graph
- Change impact report
- Incident causal graph
- Root-cause hypotheses
- Confidence scores
- Evidence links and historical references

---

## 8. MVP Scope

### Included
- Codebase ingestion and dependency graph
- Manual change submission and impact analysis
- Incident ingestion with simulated production signals
- Root-cause reasoning with explainability
- Web dashboard for visualization

### Explicitly Excluded (v1)
- Automated remediation
- Continuous live monitoring
- CI/CD enforcement or blocking
- Real-time log streaming
- Multi-cloud or multi-region orchestration

---

## 9. Success Criteria (Day 30)

SRCI is considered successful if it can:

1. Ingest a repository and build a dependency graph
2. Accept a change and predict impacted components
3. Ingest a simulated incident
4. Propose a root cause with evidence
5. Link incidents back to prior changes
6. Demonstrate the full workflow in under 5 minutes

---

## 10. Non-Goals

- Replacing observability platforms
- Acting as a general-purpose AI assistant
- Writing, deploying, or modifying production systems

---

## 11. Design Principles

- Explainability over novelty
- Structured state over conversational interfaces
- Graph-based reasoning over flat data
- Trust and auditability over automation

---

Any feature not explicitly listed in this document is **out of scope for SRCI v1**.