# PHASE 16 — Product Analysis: System Reliability & Change Intelligence (SRCI)

## 1. Product Purpose & North Star

**SRCI is an AI-powered Root Cause Analysis (RCA) and Change Intelligence platform.**

Its primary mission (North Star) is to act as an **"Autonomous SRE Copilot — a senior SRE engineer that never sleeps."** 

SRCI bridges the gap between **pre-production changes** (pre-deployment code, config, and schema updates) and **post-production incidents** (unplanned outages, latency spikes, error rate elevations). It is **not** an observability tool like Datadog or Grafana, nor is it a query dashboard. Instead, it is an **Intelligence Layer** that:
1. Translates fragmented telemetry (metrics, logs, traces) and git commits into a causal system model.
2. Traverses system dependency graphs to compute incident correlation, blast radius, and blast path.
3. Ranks root-cause hypotheses with calibrated confidence.
4. Explains AI decisions transparently, allowing SREs to audit the reasoning.
5. Implements a continuous feedback loop where human actions directly train and retrain the underlying machine learning model.

---

## 2. Target User Personas

### Primary Persona: Site Reliability Engineer (SRE)
* **Demographics**: Senior Engineer responsible for system reliability, service-level objectives (SLOs), error budgets, and incident response.
* **Core Tasks**:
  * On-call rotation.
  * Triage and mitigation of system outages.
  * Post-mortem generation and preventative action items.
  * Scaling infrastructure, capacity planning, and deployment safety gates.
* **Pain Points**:
  * **Alert Fatigue**: Flooded with raw alerts (Pagers, Slack) with zero context.
  * **Change Blindness**: Teams deploy changes to upstream dependencies without notifying downstream users, breaking APIs silently.
  * **Incident Opacity**: Investigating incidents requires jumping between multiple Datadog charts, Splunk logs, and Jaeger trace graphs, consuming valuable time.
  * **"Black Box" AI**: Distrusts typical AI solutions that give recommendations without citing evidence or explaining "why."

### Secondary Persona: Platform & Backend Engineers
* **Demographics**: Software developers building and maintaining individual microservices.
* **Core Tasks**:
  * Writing code, updating schemas, and merging pull requests.
  * Troubleshooting microservice-specific errors.
* **Pain Points**:
  * Lack of visibility into how their changes affect downstream services in production.
  * Hard to isolate if an issue is caused by their recent code push or a dependency failure.

---

## 3. User Goals & Business Value

| User Goal | How SRCI Delivers | Business Value (KPIs) |
|---|---|---|
| **Reduce MTTR (Mean Time to Resolve)** | Auto-correlates telemetry anomalies with recent changes, immediately pointing to the likely root cause change. | **Lower Downtime**: Avoids revenue loss during outages. |
| **Prevent Incidents (Safe Changes)** | Predicts blast radius and downstream failure propagation before a change is merged. | **Fewer Outages**: Higher deployment velocity with less risk. |
| **Build Operational Trust** | Explains AI ranking via structured decision traces, showing ML features, rule evaluations, and confidence bands. | **SRE Confidence**: Accelerates approval of remediation scripts. |
| **Continuous Optimization** | Integrates feedback directly back into the training data to improve prediction calibration automatically. | **System Intelligence**: The platform becomes smarter over time, custom-tailored to the organization's unique architecture. |

---

## 4. End-to-End User Journey

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Incident   │ ──> │ Correlation │ ──> │  Evidence   │ ──> │ Hypothesis  │
│  Alerting   │     │   Engine    │     │  Gathering  │     │ Formulation │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐            │
│  Learning   │ <── │  Feedback   │ <── │   Root      │ <──────────┘
│  & Retrain  │     │    Loop     │     │Cause (RCA)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

1. **Incident Trigger**: An alert is generated (e.g., via PagerDuty or direct ingestion) indicating an anomaly (e.g., "Billing API returning 500 errors").
2. **Correlation**: SRCI scans the time window before the incident and queries the system graph for changes touched by microservices, upstream nodes, or shared databases.
3. **Evidence Gather**: System links specific logs, traces, and metrics matching the window to formulate concrete evidence.
4. **Hypothesis**: The system ranks changes using a hybrid scoring algorithm (`RULE_WEIGHT` + `ML_WEIGHT`) based on graph distance, temporal proximity, service overlap, and service criticality.
5. **RCA**: The Copilot presents ranked hypotheses, explains the reasoning with citation of evidence, and proposes a dry-run or mitigation command.
6. **Feedback**: The SRE audits the prediction and submits feedback (Verdicts: `confirmed`, `rejected`, or `corrected`).
7. **Learning**: SRCI labels features, updates the database, and retrains the model when new training instances reach the threshold.

---

## 5. Existing Backend Capabilities (Reverse Engineered)

Based on the codebase analysis, SRCI possesses a robust, fully-functioning backend layer that we must expose:

1. **Ingestion & Graph Core**:
   * Services, APIs, and dependencies (YAML-defined structural relationships) are ingested into Postgres.
   * Traverses upstream and downstream relationships using a BFS traverse engine with depth levels.
2. **Deterministic Correlation (`incident_change_correlator.py`)**:
   * Rule-based engine that evaluates overlap. It checks if the services affected in the incident overlap with the services touched by recent changes within a temporal window (e.g., 24 hours).
3. **Evidence Linker (`evidence_linker.py`)**:
   * Generates evidence links for logs, metrics, and changes, matching timestamps and naming keys.
4. **Machine Learning Layer (`train_model.py`, `predictor.py`, `feature_builder.py`)**:
   * Build feature vectors: `temporal_proximity`, `service_overlap`, `graph_distance`, `criticality_score`.
   * Trains a Random Forest Classifier (`model.joblib`) to predict probability.
   * Fuses ML probability and Rule confidence using weights and reliability calibration factors.
5. **Explainability (`explanation_builder.py`, `explainer.py`)**:
   * Generates natural language analysis utilizing LLM prompts containing the context of the incident and hypotheses, falling back to a structured template if the LLM is unavailable.
6. **Escalation & Safety Guardrails (`rca_guardrails.py`, `escalation.py`)**:
   * Detects uncertainty: `weak_signal` (top score < threshold), `close_competition` (top score difference < threshold).
   * Determines confidence bands (`high`, `medium`, `low`).
   * Decides escalation status (`review_required`, `monitor`, `none`).
7. **Learning Loop (`learning_loop.py`, `feedback.py`)**:
   * Ingests feedback ratings and triggers model retraining when data increases.
