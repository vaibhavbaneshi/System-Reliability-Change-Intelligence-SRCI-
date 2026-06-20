# PHASE 16 — Master Design Document: SRE Copilot Experience

This master document compiles and synthesizes the complete user experience, information architecture, interaction flows, and accessibility patterns designed for Phase 16 of the System Reliability & Change Intelligence (SRCI) platform. 

Individual detailed design documents are linked throughout and available in the workspace:
* Detailed Product Analysis: [PHASE16_PRODUCT_ANALYSIS.md](file:///Users/vaibhavbaneshi/Desktop/System-Reliability-Change-Intelligence-SRCI-/PHASE16_PRODUCT_ANALYSIS.md)
* Information Architecture: [PHASE16_INFORMATION_ARCHITECTURE.md](file:///Users/vaibhavbaneshi/Desktop/System-Reliability-Change-Intelligence-SRCI-/PHASE16_INFORMATION_ARCHITECTURE.md)
* Incident Investigation Workflow: [PHASE16_INVESTIGATION_WORKFLOW.md](file:///Users/vaibhavbaneshi/Desktop/System-Reliability-Change-Intelligence-SRCI-/PHASE16_INVESTIGATION_WORKFLOW.md)
* RCA Workspace Design: [PHASE16_RCA_WORKSPACE_DESIGN.md](file:///Users/vaibhavbaneshi/Desktop/System-Reliability-Change-Intelligence-SRCI-/PHASE16_RCA_WORKSPACE_DESIGN.md)
* SRE Copilot Chat Design: [PHASE16_RCA_CHAT_DESIGN.md](file:///Users/vaibhavbaneshi/Desktop/System-Reliability-Change-Intelligence-SRCI-/PHASE16_RCA_CHAT_DESIGN.md)
* Weak RCA Queue Experience: [PHASE16_WEAK_RCA_DESIGN.md](file:///Users/vaibhavbaneshi/Desktop/System-Reliability-Change-Intelligence-SRCI-/PHASE16_WEAK_RCA_DESIGN.md)
* Change Intelligence Design: [PHASE16_CHANGE_INTELLIGENCE.md](file:///Users/vaibhavbaneshi/Desktop/System-Reliability-Change-Intelligence-SRCI-/PHASE16_CHANGE_INTELLIGENCE.md)
* AI Trust Layer Specifications: [PHASE16_AI_TRUST_LAYER.md](file:///Users/vaibhavbaneshi/Desktop/System-Reliability-Change-Intelligence-SRCI-/PHASE16_AI_TRUST_LAYER.md)
* Accessibility & Mobile Review: [PHASE16_ACCESSIBILITY_REVIEW.md](file:///Users/vaibhavbaneshi/Desktop/System-Reliability-Change-Intelligence-SRCI-/PHASE16_ACCESSIBILITY_REVIEW.md)

---

## 1. Information Architecture & Navigation Structure

SRCI's navigation structure is optimized for on-call triage speed and cognitive alignment. The revised structure groups the previous 11 disjointed items into 7 high-intent panels:

```
[SRCI Unified Navigation]
 ├── Dashboard (Operations Overview)
 ├── Incidents Hub (Triage Center)
 │    ├── Active Incidents (Default view)
 │    └── Weak RCA Queue (SRE Intervention view)
 ├── Change Intelligence (Pre-deployment Analysis & Timeline)
 ├── System Topology (Interactive Service Graph & Directory)
 ├── Autonomy Hub (Remediation Logs & Concurrency Workers)
 ├── Analytics & Training (Retraining loops & MTTR trends)
 └── Settings (System weights & thresholds configuration)
```

---

## 2. Dashboard Design (Operations Center)

The dashboard provides a central "control room" view for reliability teams.

### Core Layout Layout:
1. **System Health Strip (Top)**: High-level KPI status banner listing:
   * System SLO status (e.g. `99.98% / target 99.9%`).
   * MTTR performance trend sparkline.
   * Background Agent Worker Pool status (Active workers: `4/4`, concurrent locks active: `2`).
2. **Alert Area (Center-Left)**:
   * Large, high-contrast banner displayed during active outages, linking directly to the Incident Workspace.
3. **Deployments Risk Feed (Center-Right)**:
   * Real-time list of commits and configuration changes analysed by the Pre-Deployment Blast Radius Analyzer, sorting them by risk level.
4. **Integration Health Matrix (Bottom)**:
   * Grid display showing webhook telemetry ingestion health for Prometheus, Datadog, PagerDuty, and OpenTelemetry.

---

## 3. Incident Workspace

The **Incident Workspace** is the launchpad for investigation. 
* *Left Side Grid*: Displays structured metadata including ID, Title, Severity, affected core Service, incident Owner, and running duration.
* *Timeline Tree*: Vertical interactive component mapping the chronology of anomalous events leading up to and during the incident.
  * Clicking any event node (e.g., alert triggers, metric spikes) opens a detail pane displaying raw data and timestamps.
* *Milestone Loader*: Displays investigation stages during active processing to minimize operator anxiety.

---

## 4. RCA Workspace

The **RCA Workspace** is where the SRE evaluates the causal hypotheses proposed by the hybrid predictor engine.

### Layout Wireframe (ASCII):
```
┌──────────────────────────────┬──────────────────────────────────────────────┬──────────────────────────────────────────┐
│ L: INCIDENT CONTEXT (25%)    │ M: AI INVESTIGATION & RECOMMENDATIONS (50%)   │ R: DIAGNOSTICS & TRUST SIDEBAR (25%)     │
├──────────────────────────────┼──────────────────────────────────────────────┼──────────────────────────────────────────┤
│ Severity: CRITICAL           │ 🤖 CO-PILOT SUMMARY:                         │ ┌─[Tabs]───────────────────────────────┐ │
│ Service : auth-service       │ "Billing error spikes are correlated with    │ │ Trace │ Evidence (4) │ Remediation    │ │
│ Duration: 14 minutes         │ Change git:abc123def deployed 8m before."    │ └──────────────────────────────────────┘ │
│                              │                                              │                                          │
│ ┌─[Timeline]───────────────┐ │ ┌─[Rank #1 Root Cause Change]──────────────┐ │ ┌─[AI Decision Trace]──────────────────┐ │
│ │ 20:34 - 5xx Spike        │ │ │ Update auth token validation logic       │ │ │ ML Probability : 0.892 (x 0.40 wt)   │ │
│ │ 20:35 - Auto-RCA Trigger │ │ │ Service: auth-service                    │ │ │ Rule Confidence: 0.950 (x 0.60 wt)   │ │
│ │ 20:36 - Pager Alert      │ │ │ Hybrid Score: [ 0.8921 ]  (Band: HIGH)    │ │ │ Graph Penalty  : -0.054              │ │
│ └──────────────────────────┘ │ │ [ View Diff ]   [ Analyze Blast Radius ]   │ │ │ Final score    : 0.8921              │ │
│                              │ └──────────────────────────────────────────┘ │ └──────────────────────────────────────┘ │
└──────────────────────────────┴──────────────────────────────────────────────┴──────────────────────────────────────────┘
```

* **Interactive Hypothesis Cards**: Compiling descriptions, authors, overlap percentages, and scores.
* **Diagnostics Sidebar Tabs**:
  * **AI Decision Trace**: Visual tree mapping coefficients.
  * **Evidence Explorer**: Interactive log snippet viewer.
  * **Remediation & Feedback**: Code execute command blocks and SRE feedback submissions.

---

## 5. Change Intelligence Experience

Integrates post-incident correlation with pre-incident preventative gates:
1. **Pre-Deployment Blast Radius Analyzer**: Form enabling engineers to evaluate risk prior to shipping, displaying:
   * Risk score (0 to 100).
   * Visual downstream propagation path (coloring nodes by risk severity levels).
   * AI-generated warnings detailing breaking API contracts.
2. **Change Timeline**: Horizontal correlation chart linking change events (PRs, schema migrations, configs) side-by-side with incident bands to visually highlight temporal proximity.

---

## 6. SRE Copilot Chat Experience (RCA Chat)

A grounded conversational engine (Phase 16.8) designed as an integrated drawer to answer diagnostics queries:
* **Grounded Citations**: The chat outputs no uncited statements. Mentioned resources display interactive badges (e.g. `[git:abc123def]`, `[Log: L32]`) which, when clicked, automatically scroll the main page to highlight the reference.
* **Evidence Sparks**: Embeds mini metric sparkline charts and log diff blocks inside conversational bubbles.
* **Suggested Follow-Up Prompts**: Dynamic pills mapping next logical queries (e.g. *"Show git diff"*, *"Why was this change ranked above others?"*).

---

## 7. Weak RCA Queue Experience

Manages incidents flagged with `should_escalate: true` by the backend.
* **Weak RCA Triage Inbox**: Displays unresolved, high-uncertainty incidents, exposing delta scores and lock status (`auto_rca_locked_at` to prevent dual-mitigation conflicts).
* **Analyst Overrides Panel**:
  * Side-by-side comparison of competing changes.
  * Manual Evidence booster.
  * Verdict buttons: `Confirmed`, `Corrected` (manually assigning correct change), `Rejected` (AWS outages).
  * Direct webhook to trigger PagerDuty alerts on escalation.

---

## 8. AI Trust & Explainability specifications

Maps backend calculation layers to the user:
1. **Hybrid Score Dial**: Breaks down rule weight vs ML weight contributions and displays graph distance penalties.
2. **RCA Quality Checklist**: Exposes the logic inside `rca_quality.py` as a visual checklist (+10% for no close competition, +10% for evidence presence, etc.).
3. **Source Integrity Indicator**: Renders tags specifying if the explanation is `Groq LLM` or a `Template Fallback` to build model transparency.

---

## 9. Accessibility Specifications (WCAG 2.1 AA)

* **Keyboard Navigation**: Focus indicators have a high-contrast ring outline. Lock focus loops (drawers & modals) utilizing `focus-trap-react`.
* **Hotkeys Cheat-sheet**:
  * `CMD + K` / `Ctrl + K`: Toggle Copilot Chat.
  * `Esc`: Close drawer/modal.
  * `J` / `K`: Navigate queues.
  * `Alt + 1 / 2 / 3`: Quick tab switching.
* **Screen Reader ARIA attributes**:
  * SVGA graph nodes use descriptive labeling (name, status, downstream depth).
  * Milestones progress trackers wrapped in `<div aria-live="polite">` containers.

---

## 10. Mobile Strategy

* **Mobile Triage Sheet**: A responsive layout for viewports < 1024px.
* **Column Stacking**: Transposes the three-pane desktop view into a single-column layout with a top sticky segment tab navigation (`Summary`, `Hypotheses`, `Evidence`).
* **Thumb Zone Buttons**: Pins critical mitigation actions (e.g. Rollback Approve) as sticky bottom sheets. Touch targets expanded to **48px x 48px** with 8px margins.

---

## 11. P0 / P1 / P2 UX Recommendations

We recommend implementing the Phase 16 experience in three logical steps:

| Priority | UX Module | Key Features | Target Value |
|---|---|---|---|
| **P0** (Sprint 1) | **Unified Incident & RCA Workspace** | • Left Summary pane & Timeline.<br>• Center Hypothesis list.<br>• Calibrated Hybrid Score Dial.<br>• Feedback verdict submission loop (`confirmed`, `corrected`, `rejected`). | Core incident resolution. Exposes backend scores and drives the ML feedback learning loop. |
| **P1** (Sprint 2) | **Chat & Change Intelligence** | • Collapsible Slide-over SRE Copilot Chat panel.<br>• Guided Prompt Pills & Grounded Citations UX.<br>• PR Blast Radius Analyzer form & Downstream Graph.<br>• Weak RCA Queue Inbox with Lock Status Indicators. | Prevents outages before deployment and assists diagnostic deep-dives in active incident war-rooms. |
| **P2** (Sprint 3) | **Autonomy, Analytics & Accessibility** | • Autonomy Hub Worker logs & Audit Trails.<br>• Analytics retraining loop progress metrics.<br>• Keyboard hotkeys and full ARIA screen-reader mappings.<br>• Mobile responsive sheets. | Integrates platform auditability, WCAG accessibility, and allows triage capability on the go. |
