# Ingestion Module

The ingestion module is responsible for bringing system metadata into SRCI in a controlled and secure manner.

---

## Supported Inputs

- Git repositories (read-only)
- Pull requests and diffs
- Database schema metadata
- Structured logs
- Aggregated metrics
- Trace summaries

---

## Git & PR Ingestion

### Baseline Ingestion
- The main branch is treated as the system baseline
- Full structural parsing is performed once

### Change Ingestion
- Feature branches are analyzed as diffs against main
- Only changed files are reprocessed

### Access Model
- Read-only Git tokens
- No write or merge permissions

---

## Database Ingestion

SRCI ingests schema metadata only:
- Tables
- Columns
- Constraints
- Indexes

SRCI never accesses live production data rows.

---

## Logs, Metrics, and Traces

- SRCI does not stream live signals
- Signals are ingested on-demand for incident windows
- Data is normalized and correlated by timestamp and service

---

## Triggers

- Manual user action
- PR or merge event
- Incident registration