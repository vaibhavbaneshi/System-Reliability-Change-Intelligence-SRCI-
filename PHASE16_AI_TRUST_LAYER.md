# PHASE 16 — AI Trust & Explainability Experience Design

This document details the interface specifications for the **AI Trust Layer**. It translates the backend reasoning variables (`hybrid_score`, `confidence_band`, `escalation`, `weak_signal`, `quality_score`, `decision_trace`) into actionable visual representations that help SREs understand, audit, and trust the platform's outputs.

---

## 1. Trust Score Visual Architectures

### A. Calibrated Hybrid Score Dial
The `hybrid_score` combines deterministic heuristics (`rule_confidence`) and machine learning (`ml_probability`). Rather than displaying a flat score, the UI reveals the calculation:

```
[==================== 0.8921 Calibrated Hybrid Score ====================]
   Rule Contribution: 60%  [██████████████░░░░░░░░░░]  (Effective Weight: 0.60)
   ML Contribution  : 40%  [██████████░░░░░░░░░░░░░░]  (Effective Weight: 0.40)
   Graph Penalty    : -5%  [█░░░░░░░░░░░░░░░░░░░░░░░]  (Hops > 1 deduction)
```

* **Hover Interactions**:
  * Hovering over **Rule Contribution** reveals a tooltip: *"Based on 3 matching telemetry events and 2 rule checks (Reliability: 100%)."*
  * Hovering over **ML Contribution** reveals: *"Based on Random Forest Classifier output trained on 42 historical label cases (Reliability: 80%)."*
  * Hovering over **Graph Penalty** reveals: *"A deduction of -0.05 was applied because the change occurred in auth-service, which is 2 hops away from billing-service."*

### B. Confidence Band Visual Badges
The confidence band categorizes the score into actionable triage states:
* **`high` (Green Badge)**: *"Strong evidence match. Highly recommended to execute mitigation script."* (Triggered if score >= `CONFIDENCE_BAND_HIGH` default 0.70).
* **`medium` (Orange Badge)**: *"Correlation detected. Verify logs and dependency paths before rollback."* (Triggered if score >= `CONFIDENCE_BAND_MEDIUM` default 0.40).
* **`low` (Red Warning Badge)**: *"Potential weak correlation. Analyst review required."* (Triggered if score < 0.40).

---

## 2. RCA Quality Factor Checklist

The `quality_score` (computed in `rca_quality.py`) represents the robustness of the system's investigation. SREs can expand the Quality Score panel to view a checklist explaining the factors (directly mapping to the backend calculations):

```
┌─────────────────────────────────────────────────────────────┐
│ 🎖️ RCA Quality: 0.8400 (High Quality Band)                   │
├─────────────────────────────────────────────────────────────┤
│  ✅  Clear Winner Detected (No Close Competition)  [+10%]   │
│  ✅  Telemetry Evidence Present (3 Events Linked)  [+10%]   │
│  ✅  Calibrated Hybrid Score is High (> 0.75)      [+45%]   │
│  ✅  Multiple Candidates Evaluated                 [+ 5%]   │
│  ✅  No Escalation Required                        [+15%]   │
│  ⚠️  Model Confidence Band is Medium (No Bonus)    [+ 0%]   │
└─────────────────────────────────────────────────────────────┘
```

* **UX Value**: This checklist changes the system from a "black box" recommendations engine to an auditable assistant. The SRE understands exactly why the model is confident or why it flagged an incident for manual review.

---

## 3. Decision Trace & Feature Vector Visualization

The `decision_trace` data contains the `feature_snapshot`. We visualize these features using an interactive **Radar Chart** or a **Bar Grid** to compare the top hypotheses:

```
┌─[ FEATURE SNAPSHOT COMPARISON ]──────────────────────────────┐
│  Feature             │ Top Pick (auth-service) │ Runner-Up (notif) │
├──────────────────────┼─────────────────────────┼───────────────────┤
│ Temporal Proximity   │  ███████████████ 0.98   │  ███ 0.12         │
│ Service Overlap      │  █████████████░ 0.85    │  ░░░ 0.00         │
│ Graph Distance       │  1 Hop (Direct)         │  3 Hops (Remote)  │
│ Criticality Score    │  ███████████████ 1.00   │  █████████░ 0.60  │
└──────────────────────┴─────────────────────────┴───────────────────┘
```

### Explainer Transparency Indicators
At the bottom of the AI natural language explanation card, the UI displays a small metadata tag showing the generation source:
* `🤖 Generated via Groq LLM (OpenAI-calibrated)`
* `📝 Generated via Template Fallback (Rule-Based)`

This metadata ensures that SREs know if the natural language text was generated dynamically by the AI model or selected via deterministic template parsing in `explanation_builder.py`.
