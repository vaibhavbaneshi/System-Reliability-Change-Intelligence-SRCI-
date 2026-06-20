# PHASE 16 — Accessibility & Mobile Experience Review

This document defines accessibility guidelines (WCAG 2.1 AA compliance) and mobile responsive strategies for the **SRCI presentation layer**. It ensures on-call SREs can navigate triage queues and input feedback quickly across all devices and input methods.

---

## 1. Mobile Responsiveness & On-Call Triage Flows

SREs are frequently paged on the go. The desktop three-pane split screen layout must transition to a **mobile-optimized layout** for viewport widths < 1024px:

```
┌────────────────────────────────────────┐
│ INC-88219: Billing API...         [PD] │
├────────────────────────────────────────┤
│ Status: INVESTIGATING   Severity: CRIT │
├────────────────────────────────────────┤
│ ┌─[Tabs]─────────────────────────────┐ │
│ │ Summary │ Hypotheses (3) │ Evidence│ │
│ └────────────────────────────────────┘ │
│                                        │
│  🤖 AI SUMMARY CO-PILOT ANALYSIS       │
│  "Billing service is failing due to    │
│  un-closed database handles in         │
│  PR abc123def (auth-service)."         │
│                                        │
│ ┌─[Top Hypothesis Card]──────────────┐ │
│ │ Updated auth token validation      │ │
│ │ auth-service | Score: 0.892        │ │
│ │                                    │ │
│ │ [ Compare Diff ] [ Apply Revert ]  │ │
│ └────────────────────────────────────┘ │
├────────────────────────────────────────┤
│   [ Approved & Execute Rollback ]      │
└────────────────────────────────────────┘
```

* **Responsive Transposition Rules**:
  * The three-pane columns stack vertically.
  * A top sticky segment controller tabs between: `Summary`, `Hypotheses (X)`, and `Evidence`.
  * Touch targets are expanded to a minimum of **48px x 48px** with 8px gutters to prevent accidental triggers during stressful triage events.
  * Remediation buttons (e.g. Approve Rollback) are pinned as a floating, sticky bottom sheet for one-handed thumb interaction.

---

## 2. Keyboard Navigation & Hotkeys

To match SRE productivity speed (CLI-first workflows), the entire UI must be navigable using keyboard-only inputs without mouse interactions.

### Keyboard Shortcuts Reference:
* `CMD + K` or `Ctrl + K`: Toggle the SRE Copilot Chat slide-over drawer.
* `Esc`: Closes any active modals, drawer overlays, or feedback popups.
* `J` / `K`: Move highlight cursor down/up the hypothesis list or incident queue.
* `Enter` / `Space`: Open selected incident details or activate buttons.
* `Shift + Tab`: Traverse elements in reverse order.
* `Alt + 1`: Quick switch to Incidents Hub.
* `Alt + 2`: Quick switch to Change Intelligence.
* `Alt + 3`: Quick switch to System Topology.

### Focus Trapping & Visible Focus States
* Focus indicators must be highly visible and utilize offset borders to contrast against dark backgrounds:
  * CSS: `.focusable:focus { outline: none; ring: 2px solid var(--primary); ring-offset: 2px; }`
* When the feedback modal or chat slide-over drawer is opened, focus must be trapped within the container (using `focus-trap-react` behavior) to prevent keyboard users from tab-navigating elements behind the drawer.

---

## 3. Screen Reader Semantics & ARIA Schema

To support visually impaired developers and engineers, the application implements semantic HTML5 elements alongside ARIA (Accessible Rich Internet Applications) attributes:

1. **Interactive Dependency Graph**:
   * Nodes are rendered as standard HTML `<g>` containers containing `role="button"` or `role="link"`.
   * Dynamic labeling on hover:
     * `aria-label="Service node: auth-service. Health status: Degraded. Owner team: Auth-Team. Downstream connections: billing-service."`
2. **Dynamic Live Regions (`aria-live`)**:
   * The RCA milestone progress tracker (during run-RCA calculation) is wrapped in an ARIA live container:
     * `<div aria-live="polite" class="...">Analyzing pool connections...</div>`
     * Screen readers read out updates automatically as step indicators change state.
3. **Icons & Badges**:
   * System severity badges (flashing red warning icons) contain a text fallback for screen readers:
     * `<span class="bg-red-500" aria-label="Severity level: Critical Outage"></span>`
   * Score confidence badges utilize a clear label:
     * `<span aria-label="Confidence rating: 89% High">89%</span>`
