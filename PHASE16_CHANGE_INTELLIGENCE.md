# PHASE 16 — Change Intelligence Experience Design

This document details the interface and interaction design for the **Change Intelligence** modules in SRCI. It covers pre-deployment risk analysis, blast radius graph traversals, and chronological correlation systems.

---

## 1. Pre-Deployment Risk Analyzer & Blast Radius Graph

The **PR Blast Radius Analyzer** allows engineers to submit code, config, or database schema changes *before* production deployment to predict downstream failures.

### Pre-Deployment Analysis Screen (ASCII Wireframe)
```
========================================================================================================================
 [SRCI]  Dashboard  >  Change Intelligence  >  Pre-Deployment Analyzer
========================================================================================================================
 Input Target PR / Git Ref: [ https://github.com/corp/payment-service/pull/402 ]              [ Run Impact Analysis ]
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 ┌─[Risk Summary Score]────────┐ │ ┌─[Downstream Blast Radius Map (Interactive Graph)]────────────────────────────────┐
 │           [ 82 ]            │ │ │                                                                                  │
 │         HIGH RISK           │ │ │                      ┌────────────────────┐                                      │
 │                             │ │ │                      │  payment-service   │ (Root Node - Touched)                │
 │ • Impacted Services: 4      │ │ │                      └─────────┬──────────┘                                      │
 │ • Max Path Depth   : 3      │ │ │                                │ (Depth 1)                                       │
 │ • Critical Upstream: Yes    │ │ │                                ▼                                                 │
 └─────────────────────────────┘ │ │                      ┌────────────────────┐                                      │
 ┌─[AI Risk Explanation]───────┐ │ │                      │  billing-service   │ (High Risk - Direct downstream)      │
 │ "This change introduces db  │ │ │                      └─────────┬──────────┘                                      │
 │ schema adjustments in column│ │ │                                │ (Depth 2)                                       │
 │ 'txn_id' [Table: txns].     │ │ │                                ▼                                                 │
 │ Downstream billing-service  │ │ │                      ┌────────────────────┐                                      │
 │ queries this field; failure │ │ │                      │   portal-gateway   │ (Medium Risk - Transitive)               │
 │ will propagate to portal."  │ │ │                      └────────────────────┘                                      │
 └─────────────────────────────┘ │ │                                                                                  │
========================================================================================================================
```

### Downstream Traversal Logic & Visuals
* **Depth Traversal**: Visualizes the downstream traversal matching `traverse_downstream_with_depth` in the backend. 
* **Path Coloring (Blast Radius Mapping)**:
  * **Level 1 (Red)**: Direct neighbors (depth = 1) affected. Extremely high risk.
  * **Level 2 (Orange)**: Transitive neighbors (depth = 2). High risk.
  * **Level 3+ (Yellow)**: Weak downstream dependencies. Medium-to-low risk.
* **Database Dependency**: DB tables affected by schema changes are rendered as cylinder nodes (`db_table` type in DB schema) connected to services via dotted lines.

---

## 2. Change Detail View

When an engineer drills down into a specific change, the platform displays the **Change Detail Workspace**:
* **Header**: Metadata containing Author, Git Branch, Target Service (`services_touched`), and change type (`code`, `config`, `schema`).
* **Visual Diff Panel**:
  * *Code Diff*: Split-view display of code modifications.
  * *Config Diff*: Side-by-side YAML parameter comparison.
  * *Schema Diff*: Visual representation of SQL migration commands (e.g. `ALTER TABLE`, `DROP COLUMN`).
* **Impact Propagation Button**:
  * An interactive trigger that fires the backend `POST /changes/{id}/propagate` command. Clicking it runs the impact propagator and recalculates the blast radius, updating the topology map in real-time.

---

## 3. Change Timeline & Incident Correlation

To help SREs quickly spot temporal correlations during active incident investigations, SRCI provides a combined **Chronological Correlation Timeline**.

```
    [ Time Vector: Last 60 Minutes ]
    20:00                20:15                20:30                20:45                21:00
      ─────────────────────┬────────────────────┬────────────────────┬────────────────────
      CHANGES:             ● Deployed           ● Deployed                                
                           auth-service         payment-db                                
                           (git:abc123d)        (git:db772a)                              
      ────────────────────────────────────────────────────────────────────────────────────
      INCIDENTS:                                                     [════ Outage ═══════]
                                                                     INC-88219 (billing)  
                                                                     Error Rate > 15%     
      ────────────────────────────────────────────────────────────────────────────────────
      ANOMALIES:                                 ▲ Warning logged                         
                                                 DB pool exhausted                        
```

* **Timeline Mechanics**:
  * **Change Markers**: Rendered as dots (`●`). Hovering over a dot reveals a popup with Author name, deployment description, and affected files. Clicking the dot focuses the Incident list on incidents overlapping with that service.
  * **Outage Bands**: Rendered as horizontal bars spanning from `started_at` to `resolved_at`. Clicking the band opens the RCA Workspace for that incident.
  * **Anomaly Markers**: Triangles (`▲`) showing warning logs and system exceptions extracted by the evidence linker in the correlation window.
* **Correlation Highlighting**: Hovering over an active incident highlights all changes on the timeline that touch the incident's service or direct upstream dependencies within the 24-hour correlation window, visually mapping the temporal search range of `incident_change_correlator.py`.
