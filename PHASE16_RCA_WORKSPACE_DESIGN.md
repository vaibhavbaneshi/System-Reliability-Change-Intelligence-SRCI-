# PHASE 16 — RCA Workspace Design & Layout Recommendations

This document defines the interface design, panel layouts, data bindings, and UX mechanics for the **SRCI Root Cause Analysis (RCA) Workspace**. It is optimized for SRE war-rooms and fast, evidence-based triage.

---

## 1. High-Fidelity Workspace Layout (ASCII Wireframe)

The workspace utilizes a **three-pane split-screen architecture** to maximize situational awareness without requiring tab switching.

```
========================================================================================================================
 [SRCI]  Dashboard  >  Incidents  >  INC-88219 (Billing API returning 500s)                  [ On-Call SRE: Alex Chen ]
========================================================================================================================
 [L1] INCIDENT SUMMARY (25%)  │ [M1] AI EXPLANATION & HYPOTHESES (50%)       │ [R1] DIAGNOSTICS & TRUST (25%)
──────────────────────────────│──────────────────────────────────────────────│──────────────────────────────────────────
 ID: INC-88219                │ ┌──────────────────────────────────────────┐ │ ┌─[Tabs]────────────────────────────────┐
 Status: INVESTIGATING (Red)  │ │ 🤖 CO-PILOT ANALYSIS EXPLANATION         │ │ │ Trace │ Evidence (4) │ Remediation    │
 Severity: CRITICAL           │ │ "A memory retention trend in payment-    │ │ └───────────────────────────────────────┘
 Service: billing-service     │ │ queue was triggered after deployment     │ │
 Owner: Billing-Team          │ │ abc123def (auth-service) 8m before the   │ │ ┌─[Decision Trace Graph]────────────────┐
 Started: 20:34:10 (8m ago)   │ │ outage, due to un-closed processes in    │ │ │ [ml_probability: 0.892]               │
 Blast Radius: 18% Affected   │ │ transaction handlers. [Logs L28, L32]"   │ │ │    (x ML Weight: 0.40)                │
                              │ └──────────────────────────────────────────┘ │ │           +                           │
 ┌─[Event Timeline]─────────┐ │                                              │ │ [rule_confidence: 0.950]              │
 │ 20:34:10 - Alert Trigger │ │ ┌─[HYPOTHESIS 1 - Rank: #1]────────────────┐ │ │    (x Rule Weight: 0.60)              │
 │ 20:34:12 - Auto-RCA run  │ │ │ CHANGE: Updated auth token logic         │ │ │           -                           │
 │ 20:34:15 - PD Paged      │ │ │ ID: abc123def | auth-service             │ │ │ [graph_penalty: -0.054]               │
 │ 20:35:00 - Metric Spike  │ │ │ Author: Sarah M. | Code Change            │ │ │           =                           │
 │ 20:36:12 - Pod Restart   │ │ │ Hybrid Score: [ 0.8921 ]  (Band: HIGH)    │ │ │ FINAL HYBRID SCORE: [ 0.8921 ]        │
 └──────────────────────────┘ │ │ Quality: [ High (0.84) ]                 │ │ └───────────────────────────────────────┘
                              │ │ [ Inspect Diff ] [ View Blast Radius ]   │ │
                              │ └──────────────────────────────────────────┘ │ ┌─[Feature Snapshot]────────────────────┐
                              │                                              │ │ • Temporal Proximity: 0.98            │
                              │ ┌─[HYPOTHESIS 2 - Rank: #2]────────────────┐ │ │ • Service Overlap   : 0.85            │
                              │ │ CHANGE: Notification template tweak      │ │ │ • Graph Distance    : 2               │
                              │ │ ID: notif999 | notification-service      │ │ │ • Criticality Score : 0.60            │
                              │ │ Hybrid Score: [ 0.1245 ]  (Band: LOW)     │ │ └───────────────────────────────────────┘
                              │ └──────────────────────────────────────────┘ │
                              │                                              │ [ Close Sidebar ]
========================================================================================================================
```

---

## 2. Panel Specifications & Functional Components

### A. Left Pane: Incident Summary & Event Timeline
* **Metadata Panel**: Standardized metrics. Displaying severity badges with animated breathing glows for active incidents.
* **Incident Timeline**: A vertical tree showing raw sequential events.
  * *UI Element*: Collapsible timeline nodes colored by telemetry type (Red Alert icon, Yellow Warning icon, Blue Ingestion icon).

### B. Middle Pane: Copilot Explanation & Causal Hypotheses
* **AI Summary Panel**: A glassmorphic banner containing the LLM-generated explanation.
  * *UX Rule*: Inline link citations mapping directly to telemetry records in the evidence panel (e.g., clicking `[Logs L28]` opens the corresponding logs inside the Evidence tab).
* **Hypothesis Ranking Queue**: Rendered as a stacked list ordered by `hybrid_score`.
  * *Visual Badges*:
    * **Confidence Band**: Red for `low` (<0.3), Orange for `medium` (0.3 - 0.7), Green for `high` (>=0.7).
    * **Quality Band**: Shows composite `quality_score` (calculated in `rca_quality.py`).
  * *Actions in Hypotheses Cards*:
    * `Compare Diff`: Launches a side-by-side git diff view.
    * `View Blast Radius`: Links to the change impact analysis graph.

### C. Right Pane: Diagnostics, Trust & Remediation (Tabbed)
* **Tab 1: Decision Trace (AI Trust Layer)**:
  * Visualizes the formulas in `predictor.py` and `hybrid_scorer.py`.
  * Shows how the weights (`RULE_WEIGHT` and `ML_WEIGHT`) combine with model features to produce the final score.
  * Shows the **Graph Distance Penalty** if the change is not direct (graph distance > 1).
* **Tab 2: Evidence Explorer**:
  * An interactive filter panel allowing search by data source (`log`, `metric`, `trace`).
  * Telemetry graphs (latency curves, CPU charts, log blocks) matching the time window.
* **Tab 3: Remediation & Feedback**:
  * Proposes the mitigation script.
  * Interactive buttons for `Dry-run Simulation` and `Approve & Execute`.
  * **Feedback Block**: Direct interface for learning loop:
    * Select verdict: `Confirmed`, `Corrected` (with dropdown to select other change), `Rejected`.
    * Comment textarea for notes.
    * Submit button that calls `POST /incidents/{incident_id}/feedback`.

---

## 3. Interaction Mechanics

1. **Side-by-Side Verification**: Clicking a Hypothesis card in the middle pane automatically focuses and updates the Decision Trace and Evidence Explorer in the right pane.
2. **Milestone Loading Progression**: When `isAnalyzing` is active (e.g. during re-running RCA), the center pane displays the custom `InvestigationProgress` component with concrete milestones (`Data collection`, `Pattern identification`, etc.) to alleviate cognitive load.
3. **Calibrated Clamping & Alerts**: If `escalation.should_escalate` is true, a warnings banner is anchored at the top of the middle pane, explicitly explaining the reasons (e.g., "AI is uncertain: multiple candidates scored closely").
