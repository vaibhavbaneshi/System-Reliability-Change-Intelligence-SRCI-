# PHASE 16 — Incident Investigation Workflow Design

This document details the end-to-end incident investigation workflow in SRCI, aligning human operators (SREs) with autonomous backend agents. 

---

## 1. High-Level Flow Chart

```
  [1. TRIGGER]       [2. INVESTIGATE]      [3. MITIGATE]         [4. LEARN]
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Alert Ingest │ ──> │ Explore RCA  │ ──> │ Dry-Run /    │ ──> │ Submit       │
│ & Queue Flag │     │ Workspace    │     │ Execute Script│    │ Feedback     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
  • Ingest Event       • AI Explanation     • Revert deployment   • Confirm RCA
  • Auto-correlate     • Compare diffs      • Scale pod replicas  • Correct RCA
  • Escalate (if low)  • Check AI Trace     • Close incident      • Retrain ML
```

---

## 2. Step-by-Step Incident Investigation Loop

### Step 1: Trigger & Triage (Alert Reception)

* **Goal**: Detect an incident, trigger autonomous correlation, and alert the on-call engineer.
* **System Actions**:
  1. Incident ingested via webhook (`POST /incidents/ingest`) from Datadog, PagerDuty, or OpenTelemetry.
  2. Ingestion trigger starts `autonomy/monitor.py` which calls `POST /incidents/{id}/run-rca` to execute the pipeline:
     * Correlates logs/metrics in the time window (`incident_change_correlator.py`).
     * Compiles evidence (`evidence_linker.py`).
     * Extracts ML features (`feature_builder.py`).
     * Performs prediction (`predictor.py`) and computes hybrid score.
     * Evaluates escalation rules (`escalation.py`).
  3. If escalation is flagged (due to `weak_signal`, `close_competition`, or low confidence), the system fires a PagerDuty alert and queues it under the **Weak RCA Queue** in SRCI. Otherwise, it lands in the **Active Incidents Queue**.
* **SRE Actions**:
  * Receives pager alert, opens the SRCI Dashboard, and clicks the incident in the **Incidents Queue**.
* **Target Screen**: **Incidents Hub (Queue View)**.

---

### Step 2: Investigation & Diagnostics

* **Goal**: Understand the incident, evaluate evidence, and review the AI-suggested root cause.
* **Target Screen**: **Unified Incident & RCA Workspace**.
* **SRE Experience**:
  * SRE views the **Incident Summary** (blast radius, duration, affected services) on the left side pane.
  * SRE reviews the **AI Explanation Panel** in the center pane (natural language breakdown of the issue, citing logs and code changes).
  * SRE analyzes the **Hypothesis Ranking** list. The top hypothesis is highlighted with its **Confidence Band** (High/Medium/Low) and **Quality Score** (0.0 to 1.0).
* **Decision Point 1**: *Do I trust the top hypothesis?*
  * **Action**: SRE clicks on the **AI Decision Trace** tab to audit the prediction:
    * Views the feature weights (Rule Weight vs ML Weight).
    * Inspects the feature vector (temporal proximity, service overlap, graph distance, criticality).
    * Views the graph penalty deduction if the change occurred in a downstream component.
  * **Action**: SRE clicks on the **Telemetry & Logs** tab to view log snippets, metric metrics, and traces cited as supporting evidence.

---

### Step 3: Mitigation & Validation

* **Goal**: Take operational action to restore service health.
* **Target Screen**: **RCA Workspace (Remediation Tab)**.
* **SRE Experience**:
  * The SRE reviews the AI-generated remediation command block (e.g., `kubectl scale deployment auth-service --replicas=6` or a Rollback Git script).
* **Decision Point 2**: *Is the proposed script safe to run?*
  * **Action A (Dry Run)**: SRE clicks **Dry Run Simulation**. 
    * The backend evaluates potential side effects on the dependency graph and returns a risk projection (e.g., "Expected memory drop: 1.4GB. Estimated downtime risk: 0%").
  * **Action B (Execute)**: SRE clicks **Approve & Execute**.
    * The platform runs the remediation script against production.
    * SRE monitors live service status indicators in the workspace.
    * If the service is restored, status transitions to `resolved`.
    * If the service degrades further, SRE clicks **Rollback Execution** to revert.
  * **Action C (Manual Bypass)**: SRE executes custom mitigation outside SRCI (e.g. manually restarting DB), then returns to SRCI to mark the incident as `resolved`.

---

### Step 4: Closing the Loop (Feedback & Retraining)

* **Goal**: Log feedback on AI accuracy and retrain ML models to prevent future failures.
* **Target Screen**: **RCA Workspace (Feedback Modal)**.
* **SRE Experience**:
  * Once the incident is resolved, a feedback panel appears demanding user verification of the root cause.
* **Decision Point 3**: *How accurate was the AI-suggested root cause?*
  * **Option A: Confirmed (Accurate)**:
    * *SRE Action*: Selects the top recommended change and clicks **Confirm**.
    * *System Action*: Submits `verdict=confirmed` and `change_id`. The backend marks this change as positive (`label=1`) and all other competing changes as negative (`label=0`).
  * **Option B: Corrected (Incorrect recommendation, correct change listed)**:
    * *SRE Action*: SRE identifies that change #3 in the list was the true cause. They select change #3 and click **Correct**.
    * *System Action*: Submits `verdict=corrected` and `change_id`. The backend marks change #3 as positive (`label=1`) and all others (including the AI's top pick) as negative (`label=0`).
  * **Option C: Rejected (Completely wrong recommendation, or external cause)**:
    * *SRE Action*: SRE indicates none of the changes caused the issue (e.g., AWS outage). Clicks **Reject**.
    * *System Action*: Submits `verdict=rejected`.
* **System Learning Loop**:
  * The feedback endpoint triggers `maybe_retrain()`. If the minimum labeled samples count (`MIN_LABELS_FOR_RETRAIN`) is satisfied and the classes are balanced, the backend trains a new RF model, saving it as `model.joblib`.
  * The SRE is notified of the model update on the Analytics dashboard.
