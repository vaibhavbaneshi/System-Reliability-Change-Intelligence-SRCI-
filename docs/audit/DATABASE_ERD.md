# DATABASE_ERD.md

**Database:** PostgreSQL 15 (`srci`)  
**Domain:** System Reliability & Change Intelligence

---

## Entity Relationship Explanation

SRCI models a **dependency graph** of engineering services connected by directed edges. Changes propagate impact through this graph. Incidents attach to affected services, and the system correlates incidents with recent changes to produce ranked root-cause hypotheses. ML features capture the statistical relationship between incident–change pairs.

### Core Entity Groups

| Group | Tables | Role |
|-------|--------|------|
| **Service Catalog** | `services`, `apis`, `db_tables` | Registry of system components |
| **Graph** | `dependencies` | Directed edges between components |
| **Change Domain** | `changes`, `change_impacts` | Change events and blast radius |
| **Incident Domain** | `incidents`, `incident_entities`, `evidence` | Failure events and supporting data |
| **Intelligence** | `root_cause_hypotheses`, `incident_change_features` | Correlation output and ML features |

### Relationship Types

| Type | Example | Mechanism |
|------|---------|-----------|
| **Direct FK** | `apis.service_id → services.id` | Enforced in DDL |
| **Polymorphic** | `dependencies.source_id` | Application-level resolution via `source_type` |
| **Logical FK** | `root_cause_hypotheses.change_id → changes.id` | Joined in Python, not enforced |
| **Junction (implicit)** | `incident_change_features` | Links incidents to changes with computed features |

---

## Parent / Child Table Map

| Parent | Child | Relationship | FK Enforced |
|--------|-------|--------------|-------------|
| `services` | `apis` | 1:N | Yes |
| `services` | `dependencies` (as source/target) | 1:N polymorphic | No |
| `db_tables` | `dependencies` (as target) | 1:N polymorphic | No |
| `changes` | `change_impacts` | 1:N | Yes |
| `incidents` | `incident_entities` | 1:N | Yes |
| `incidents` | `root_cause_hypotheses` | 1:N | Yes |
| `incidents` | `evidence` | 1:N | Yes |
| `incidents` | `incident_change_features` | 1:N | No |
| `changes` | `incident_change_features` | 1:N | No |
| `changes` | `root_cause_hypotheses` | 1:N | No |

---

## Full Entity Relationship Diagram

```mermaid
erDiagram
    services {
        uuid id PK
        text name UK
        text owner_team
        text criticality
        timestamp created_at
    }

    apis {
        uuid id PK
        uuid service_id FK
        text path
        text method
        timestamp created_at
    }

    db_tables {
        uuid id PK
        text name
        text schema_name
        timestamp created_at
    }

    dependencies {
        uuid id PK
        text source_type
        uuid source_id
        text target_type
        uuid target_id
        text dependency_type
        timestamp created_at
    }

    changes {
        uuid id PK
        text change_type
        text description
        text git_ref
        timestamp created_at
    }

    change_impacts {
        uuid id PK
        uuid change_id FK
        text entity_type
        uuid entity_id
        text impact_level
        timestamp created_at
    }

    incidents {
        uuid id PK
        text title
        text severity
        timestamp started_at
        timestamp resolved_at
        timestamp created_at
    }

    incident_entities {
        uuid id PK
        uuid incident_id FK
        text entity_type
        uuid entity_id
    }

    root_cause_hypotheses {
        uuid id PK
        uuid incident_id FK
        uuid change_id
        text description
        float confidence
        timestamp created_at
    }

    evidence {
        uuid id PK
        uuid incident_id FK
        text source_type
        text reference
        timestamp created_at
    }

    incident_change_features {
        uuid id PK
        uuid incident_id
        uuid change_id
        float temporal_proximity
        float service_overlap
        float graph_distance
        float criticality_score
        int label
        timestamp created_at
    }

    services ||--o{ apis : "has"
    services ||--o{ dependencies : "source"
    services ||--o{ dependencies : "target"
    db_tables ||--o{ dependencies : "target"
    changes ||--o{ change_impacts : "impacts"
    changes ||--o{ root_cause_hypotheses : "candidate cause"
    changes ||--o{ incident_change_features : "features"
    incidents ||--o{ incident_entities : "affects"
    incidents ||--o{ root_cause_hypotheses : "hypothesizes"
    incidents ||--o{ evidence : "has"
    incidents ||--o{ incident_change_features : "features"
```

---

## Dependency Graph Sub-Diagram

The dependency graph is the central structural element. Edges are polymorphic but current ingestion only creates `service → service` edges.

```mermaid
erDiagram
    services ||--o{ dependencies : "source (service)"
    services ||--o{ dependencies : "target (service)"
    apis ||--o{ dependencies : "source (api)"
    db_tables ||--o{ dependencies : "target (db_table)"

    services {
        uuid id PK
        text name
        text criticality
    }

    dependencies {
        uuid source_id
        text source_type
        uuid target_id
        text target_type
        text dependency_type
    }
```

**Graph Semantics:**

- `source_id` depends on `target_id` (source calls/consumes target)
- Impact propagation walks from target → source (downstream callers)
- Graph traversal for RCA expands affected services downstream

---

## Change Impact Flow Diagram

```mermaid
erDiagram
    changes ||--o{ change_impacts : "direct + propagated"
    change_impacts }o--|| services : "entity (service)"
    change_impacts }o--|| apis : "entity (api)"
    change_impacts }o--|| db_tables : "entity (db_table)"

    changes {
        uuid id PK
        text change_type
        text git_ref
    }

    change_impacts {
        uuid change_id FK
        text entity_type
        uuid entity_id
        text impact_level
    }
```

**Impact Levels:**

- `high` — directly touched by change
- `medium` — one hop downstream in dependency graph
- `low` — two or more hops downstream

---

## Incident Correlation Flow Diagram

```mermaid
erDiagram
    incidents ||--o{ incident_entities : "directly affected"
    incident_entities }o--|| services : "entity"
    incidents ||--o{ root_cause_hypotheses : "ranked causes"
    root_cause_hypotheses }o--|| changes : "candidate"
    incidents ||--o{ incident_change_features : "ML features"
    incident_change_features }o--|| changes : "scored against"
    incidents ||--o{ evidence : "supporting data"

    incidents {
        uuid id PK
        timestamp started_at
        text severity
    }

    root_cause_hypotheses {
        uuid incident_id FK
        uuid change_id
        float confidence
    }

    incident_change_features {
        uuid incident_id
        uuid change_id
        float temporal_proximity
        float service_overlap
        float graph_distance
        float criticality_score
    }
```

---

## Polymorphic Entity Resolution

Several tables use a `(entity_type, entity_id)` pattern without database-level FK enforcement:

| Table | entity_type Values | Resolves To |
|-------|-------------------|-------------|
| `dependencies` | `source_type`: service, api | `services`, `apis` |
| `dependencies` | `target_type`: service, db_table | `services`, `db_tables` |
| `change_impacts` | service, api, db_table | `services`, `apis`, `db_tables` |
| `incident_entities` | service, api, db_table | `services`, `apis`, `db_tables` |

This design allows graph flexibility but creates **referential integrity risk** — orphaned UUIDs are possible if entities are deleted without cascade cleanup.
