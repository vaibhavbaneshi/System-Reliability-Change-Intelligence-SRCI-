# PHASE 16 — Weak RCA Experience Design

This document details the interface and operations workflows for **Weak RCA Queue** and **Analyst Intervention**. These features handle high-uncertainty incidents (flagged by the backend escalation engine) where human judgment is needed to resolve ambiguity and retrain the models.

---

## 1. Triggering Logic (Reverse-Engineered Backend Rules)

An incident is routed to the Weak RCA Queue if the backend `evaluate_escalation()` returns `should_escalate: true`. The triggers are:

```
                  ┌─────────────────────────────────────┐
                  │        Incident Ingested            │
                  └─────────────────────────────────────┘
                                     │
                                     ▼
                      [ Run-RCA Engine Computations ]
                                     │
            ┌────────────────────────┴────────────────────────┐
            ▼ (Any conditions met?)                           ▼ (None met)
 ┌──────────────────────────────────────┐          ┌───────────────────────┐
 │ 1. hybrid_score < ESCALATION_THRESH  │          │                       │
 │ 2. confidence_band == 'low'          │          │   Route to            │
 │ 3. weak_signal (top score < 0.35)    │ ───>     │   Active Incidents    │
 │ 4. close_competition (delta < 0.10)  │          │   Queue               │
 └──────────────────────────────────────┘          └───────────────────────┘
                    │
                    ▼
     Route to [ WEAK RCA QUEUE ]
     + Evaluate PagerDuty routing
     + Lock incident concurrency via auto_rca_locked_at
```

---

## 2. The Weak RCA Queue Interface

The Weak RCA Queue is a high-priority inbox within the Incidents Hub. It lists incidents where the AI agent is uncertain.

### Inbox Grid Fields:
1. **Status Icon**: Red warning exclamation mark indicating review is required.
2. **Incident ID & Title**: E.g., `INC-4091: payment-service latency degradation`.
3. **Escalation Reasons**: Badges showing:
   * `[Weak Signal]`: Top candidate score below strong-evidence threshold.
   * `[Close Competition]`: Multiple changes scored similarly (e.g., `delta = 0.021`).
   * `[Low Confidence]`: Top score is under 0.3.
4. **Competing Candidates count**: Number of changes flagged in the time window (e.g., `3 changes`).
5. **Lock Status (`auto_rca_locked_at`)**:
   * *UX Visual*: A padlock icon showing if another SRE is currently investigating this incident, listing their name and time locked (e.g., `Locked by Sarah M. 4m ago`). This prevents dual-mitigation conflicts.

---

## 3. Analyst Intervention Workflow

When an SRE clicks on a Weak RCA incident, they enter the **Intervention Workspace**.

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ⚠️ TRIAGE ACTION REQUIRED: The AI Copilot is uncertain about the root cause of this incident.    │
│  Reason: Close competition detected between Change #1 and Change #2 (Score delta: 0.015)          │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Intervention Actions:

#### 1. Split-View Comparison Card
* Displays the two competing changes side-by-side:
  * **Change #1 (AI Top Pick)**: Deployed 12m ago, touches `auth-service` (indirect upstream dependency).
  * **Change #2 (Runner-Up)**: Deployed 10m ago, touches `database-migration` (shared DB table `transactions`).
* Shows the feature vector variables side-by-side to allow the analyst to spot the subtle signal difference.

#### 2. Manual Evidence Booster
* If the SRE discovers an external signal not linked by the automated pipeline (e.g. a specific log stack trace), they can click **Link Manual Evidence**.
* They paste the log text or select a metric from a dropdown. This recalculates the `evidence_count` and rule confidence, prompting the SRE to click **Re-Run RCA**.

#### 3. Overriding & Labeling (Learning Loop Entry)
* The SRE resolves the incident by selecting the true cause:
  * **Action: Accept Overridden Candidate**:
    * SRE selects the runner-up change card and clicks **Mark as True Root Cause**.
    * This submits a `corrected` verdict to `/feedback`, forcing the database to save `label=1` for the runner-up and `label=0` for the default top pick.
  * **Action: Dismiss AI Candidates**:
    * SRE determines that none of the changes caused the issue (e.g. AWS S3 network failure).
    * SRE clicks **Reject All Recommendations**.
    * Submits `verdict=rejected` to `/feedback`, skipping label assignment but adding to retrain metrics.

---

## 4. Escalation Workflow (When Analyst is Stuck)

If the triaging SRE cannot determine the root cause:
1. **Assign to Service Owner**: SRE clicks `Escalate to Owner`. The platform automatically identifies the owner of the affected service (from the `services.owner_team` database column), sends a Slack ping containing the incident workspace link, and assigns ownership.
2. **Sync to Observability**: SRE clicks `Post Event to Datadog`. Annotates the active Datadog metric timeline with a vertical bar showing that SRCI is investigating a Weak RCA for the outage.
