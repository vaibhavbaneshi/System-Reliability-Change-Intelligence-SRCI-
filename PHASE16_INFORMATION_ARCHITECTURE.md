# PHASE 16 — Information Architecture & Navigation Design

## 1. Audit of Current Navigation

The current application contains 11 top-level navigation items. While functional, it imposes a high cognitive load, separating closely linked concepts (e.g., showing Incident detail on one page, RCA hypotheses on another, and Decision Traces on a third).

| Current Nav | Status | Decision & Rationale |
|---|---|---|
| **Dashboard** | **Kept** | Retained as the central operations room, showing active outages, worker pool statistics, and system health summaries. |
| **Incidents** | **Merged** | Merges with RCA, Weak RCA, and Feedback loops into a unified **Incidents Triage Hub**. |
| **RCA** | **Merged** | Removed as a top-level page. The Root Cause Analysis is the core workspace within an individual incident's detail view. |
| **Weak RCA** | **Merged** | Moved as a specialized tab/queue inside the **Incidents Triage Hub**. It does not warrant a top-level tab. |
| **Services** | **Merged** | Combined with the dependency graph into a unified **System Topology** directory. |
| **Changes** | **Redesigned**| Expanded into **Change Intelligence**, combining the historical Change Timeline and pre-deployment Blast Radius Impact Analyzer. |
| **Decision Trace** | **Merged** | Removed as a top-level nav. The AI decision trace is contextual and must be displayed inside the RCA workspace to explain specific hypotheses. |
| **Autonomous Actions**| **Redesigned**| Renamed to **Autonomy Hub** to monitor background worker logs, concurrent runs, lock releases, and integration status (PagerDuty, Datadog). |
| **Knowledge Base** | **Removed** | Decompressed. Learning feedback logs are moved to the Analytics page under training metrics. |
| **Analytics** | **Expanded** | Renamed to **Analytics & Training Loop** to monitor MTTR metrics, label generation rate, and ML model retraining stats. |
| **Settings** | **Kept** | Consolidates config settings (scoring weights, threshold adjustments). |

---

## 2. Redesigned Information Architecture (IA)

The ideal IA groups functions by **intent** and follows the natural workflow of an SRE:
* **Dashboard** (System Health & Operations Status)
* **Incidents Hub** (Active Incident Investigation & Escalated Weak RCAs)
* **Change Intelligence** (Pre-deployment Analysis & Change History)
* **System Topology** (Interactive Graph & Service Registry)
* **Autonomy Hub** (Monitoring background agents & connections)
* **Analytics & Training** (Model Health & Training Data Calibration)
* **Settings** (Weights, thresholds, alerts)

```
[SRCI Navigation]
 ├── Dashboard
 ├── Incidents Hub
 │    ├── Active Incidents Queue
 │    ├── Weak RCA (Review Queue)
 │    └── Incidents Archive
 ├── Change Intelligence
 │    ├── Blast Radius Analyzer
 │    └── Change Timeline
 ├── System Topology
 │    ├── Interactive Dependency Graph
 │    └── Service Registry
 ├── Autonomy Hub
 ├── Analytics & Training
 └── Settings
```

---

## 3. Top-Level Page Specifications

### A. Dashboard (Operations Center)
* **Objective**: Fast overview of system reliability and background copilot activity.
* **Core Widgets**:
  1. *Active Incident Alert Banner*: Shows severity and MTTR counter.
  2. *Copilot Agent Status Card*: Shows active workers, distributed locking status, database lock duration, and queue health.
  3. *Risk Heatmap*: Recent deployments flagged by the Change Blast Radius Analyzer.
  4. *Integration Health Grid*: Quick status indicator (Green/Red) of Datadog, PagerDuty, Prometheus, and OpenTelemetry streams.

### B. Incidents Hub
* **Objective**: The workspace for active triaging and root cause determination.
* **Active Incidents Queue**: Filters incidents by severity (`critical`, `high`, `medium`, `low`) and ownership.
* **Weak RCA Queue**: A dedicated inbox for incidents flagged with `weak_signal` or `close_competition` where the AI agent is uncertain and demands human confirmation. This replaces the isolated Weak RCA page.

### C. Change Intelligence
* **Objective**: Investigate changes pre-deployment and post-deployment.
* **PR Blast Radius Analyzer**: An interactive form where engineers submit Git refs, configuration JSONs, or DB Schema diffs to view downstream blast radius and risk scores prior to shipping.
* **Change Timeline**: Chronological directory of all commits, configuration changes, and schema updates.

### D. System Topology
* **Objective**: Explorable service maps.
* **Interactive Dependency Graph**: Force-directed SVG model showing microservices, APIs, database tables, and communication channels (colored by health status or depth levels from a selected node).
* **Service Registry**: Flat table detail for search, listing owners, SLA metrics, and dependency metrics.

### E. Autonomy Hub
* **Objective**: Log tracer of actions taken autonomously.
* **Worker Logs**: Real-time worker execution streams.
* **Remediation Audit Trail**: Logs of all script approvals, executions, dry-runs, and rollbacks.

### F. Analytics & Training
* **Objective**: Explain the performance of the system and ML models.
* **MTTR Trend Charts**: Shows historical progression of resolution speeds.
* **Feedback Loop Tracker**: Logs label count progress (e.g., "18/20 labels collected for retraining") and details on the last model update.
* **Feature Weights Panel**: Displays active coefficients for ML probability vs rule confidence.
