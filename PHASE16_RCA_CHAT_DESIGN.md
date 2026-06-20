# PHASE 16 — RCA Chat Experience Design

This document details the conversational experience design (Phase 16.8) for the **SRCI SRE Copilot Chat**. It focuses on grounded, evidence-backed explanations rather than open-ended chatbot behaviors.

---

## 1. Chat Layout & Interface Integration

The chat interface is designed to support the SRE where they work, operating in **dual modes**:
1. **Collapsible Slide-over Panel (Active Triage)**: Opens as a drawer on the right side of the Incident Workspace, occupying 30% of the screen. SREs can ask questions while viewing the graph and timeline.
2. **Dedicated Chat Page (Post-Mortem & Deep-Dive)**: Full-screen terminal-like workspace for reviewing system-wide changes, writing post-mortems, or comparing different deployment days.

### Chat Window Layout (ASCII Wireframe)
```
┌────────────────────────────────────────────────────────┐
│ 🤖 SRE Copilot Chat                               [ X ] │
├────────────────────────────────────────────────────────┤
│ Copilot: I am analyzing INC-88219. The billing service │
│ is experiencing a 15% error spike correlated with a    │
│ code change in auth-service.                           │
│                                                        │
│ User: Why is billing failing?                          │
│                                                        │
│ Copilot: The billing service depends on auth-service   │
│ for token validation [View Topology]. An error spike   │
│ in auth-service [Metric Trace] is propagating          │
│ downstream, causing connection timeouts [Log: L42].    │
│                                                        │
│ ┌─[Evidence Citation]────────────────────────────────┐ │
│ │ Metric: Auth Service 5xx Spiked to 18.2%           │ │
│ │ [Show Metric Chart]                                │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│ User: What changed before this outage?                 │
│                                                        │
│ Copilot: Sarah M. merged PR #405: "Updated auth token  │
│ validation logic" [git:abc123def] 8 minutes before     │
│ the incident started.                                  │
├────────────────────────────────────────────────────────┤
│ [Pill: Show git diff] [Pill: Why is confidence high?]  │
├────────────────────────────────────────────────────────┤
│ > Ask a follow-up question...                      [>] │
└────────────────────────────────────────────────────────┘
```

---

## 2. Conversation & Interaction Features

### A. Context-Aware Suggested Prompts (Dynamic Pills)
At the bottom of the chat window, SRCI displays contextual prompt pills based on the current state of the investigation.

* **On Opening**:
  * *"Why is [service_name] failing?"*
  * *"What changed before this outage?"*
  * *"Are there downstream dependencies affected?"*
* **After selecting a hypothesis**:
  * *"Explain confidence score for this change."*
  * *"Why was change X ranked higher than Y?"*
  * *"Show me the Git diff for change X."*
* **After service recovery**:
  * *"Draft an incident post-mortem."*
  * *"Suggest preventative health gates."*

### B. Citation UX & Evidence References
To prevent LLM hallucination and build trust, the chat implements strict citation rules:
* **Rule 1: No Uncited Claims**: Every explanation of a metric anomaly or log error must display an interactive citation badge.
* **Citation Badges Schema**:
  * Code Change badge: `[git:ref]` (e.g. `[git:abc123def]`). Clicking opens the Git Diff modal.
  * System Graph badge: `[View Topology]`. Clicking highlights the node in the interactive dependency graph on the main page.
  * Log badge: `[Log: ID]`. Clicking highlights the exact raw log line in the Evidence tab.
  * Metric badge: `[Metric: Name]`. Hovering reveals a mini sparkline chart of the metric trend.

### C. Rich Evidence Cards
When the user asks, *"Show supporting evidence,"* the chat does not output text blocks. Instead, it embeds rich cards inside the stream:
* **Metric Sparkline Card**: Displays a timeline trend of CPU usage or database connection pools showing when the spike crossed the standard deviation line.
* **Log Diff Card**: Displays JSON logs side-by-side highlighting the exceptions.

---

## 3. Dynamic Follow-Up Flow: "Explain Confidence Score"

When the user clicks the pill **"Explain confidence score"**, the chat provides a structured breakdown:

1. **Natural Language Explanation**: *"The hybrid score is 0.892. This is based on a high ML probability (89%) and strong rule confidence. The change modified `auth-service`, which directly touches `billing-service` (100% service overlap) and was deployed 8 minutes before the first 500 error."*
2. **Causal Logic Traversal**:
   * Displays the Decision Trace variables:
     * `temporal_proximity`: `0.98` (Spiked immediately after merge)
     * `service_overlap`: `1.0` (Direct dependency call path)
     * `graph_distance`: `1` (Direct neighbor)
     * `criticality_score`: `1.0` (Auth is a P0 critical gateway)
3. **Competing Hypotheses Comparison**:
   * Question: *"Why was change X ranked higher?"*
   * Answer: *"Change X (`abc123def`) had a graph distance of 1 (direct neighbor) to the failing service, whereas Change Y (`notif999`) had a graph distance of 3 (downstream notification template) and did not share DB pools."*
