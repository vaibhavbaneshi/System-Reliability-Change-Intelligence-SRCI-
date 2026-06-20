# DATABASE_INVENTORY.md

**Database:** PostgreSQL 15  
**Database Name:** `srci`  
**Schema Sources:** `backend/app/migrations/versions/*.sql`  
**Migration Runner:** `scripts/run_migrations.sh`

---

## Summary by Object Type

| Object Type | Count | Notes |
|-------------|-------|-------|
| Extensions | 1 | `uuid-ossp` |
| Tables | 11 | All in migration SQL |
| Views | 0 | None defined |
| Materialized Views | 0 | None defined |
| Sequences | 0 | UUID via `uuid_generate_v4()` |
| Triggers | 0 | None defined |
| Functions | 0 | No user-defined functions |
| Stored Procedures | 0 | None defined |
| Explicit Indexes | 0 | Only implicit PK/UNIQUE indexes |
| Explicit Foreign Keys | 5 | See constraint section |

---

## Extensions

### `uuid-ossp`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Provides `uuid_generate_v4()` for UUID primary key defaults |
| **Defined in** | `initial_schema.sql` |
| **Dependencies** | Required by all tables with `DEFAULT uuid_generate_v4()` |

---

## Tables

### 1. `services`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Core service registry — system of record for microservices in the dependency graph |
| **Defined in** | `initial_schema.sql` |
| **Business Usage** | Ingestion, graph traversal, ML criticality scoring, API listing |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `name` | TEXT | NOT NULL | — | UNIQUE |
| `owner_team` | TEXT | YES | — | |
| `criticality` | TEXT | YES | — | CHECK: `low`, `medium`, `high` |
| `created_at` | TIMESTAMP | NOT NULL | `NOW()` | |

**Primary Key:** `id`  
**Foreign Keys:** None  
**Referenced By:** `apis.service_id`, `dependencies` (polymorphic), `change_impacts`, `incident_entities`

---

### 2. `apis`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | API endpoint metadata per service (optional, future-safe) |
| **Defined in** | `initial_schema.sql` |
| **Business Usage** | Not populated by current ingestion; schema reserved for future use |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `service_id` | UUID | YES | — | FK → `services(id)` ON DELETE CASCADE |
| `path` | TEXT | NOT NULL | — | |
| `method` | TEXT | NOT NULL | — | |
| `created_at` | TIMESTAMP | NOT NULL | `NOW()` | |

**Primary Key:** `id`  
**Foreign Keys:** `service_id` → `services(id)` ON DELETE CASCADE

---

### 3. `db_tables`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Database table metadata (schema metadata ingestion) |
| **Defined in** | `initial_schema.sql` |
| **Business Usage** | Not populated by current ingestion; schema reserved for future use |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `name` | TEXT | NOT NULL | — | |
| `schema_name` | TEXT | YES | — | |
| `created_at` | TIMESTAMP | NOT NULL | `NOW()` | |

**Primary Key:** `id`  
**Foreign Keys:** None

---

### 4. `dependencies`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Graph core — service/API → service/db_table dependency edges |
| **Defined in** | `initial_schema.sql` |
| **Business Usage** | Dependency listing, impact propagation, graph traversal for RCA |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `source_type` | TEXT | YES | — | CHECK: `service`, `api` |
| `source_id` | UUID | NOT NULL | — | Polymorphic FK (no DB constraint) |
| `target_type` | TEXT | YES | — | CHECK: `service`, `db_table` |
| `target_id` | UUID | NOT NULL | — | Polymorphic FK (no DB constraint) |
| `dependency_type` | TEXT | YES | — | e.g. `runtime`, `sync_api`, `http`, `grpc` |
| `created_at` | TIMESTAMP | NOT NULL | `NOW()` | |

**Primary Key:** `id`  
**Foreign Keys:** None (polymorphic design)  
**Logical Dependencies:** `source_id` → `services` or `apis`; `target_id` → `services` or `db_tables`

---

### 5. `changes`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Change events — PRs, commits, schema changes, config changes |
| **Defined in** | `initial_schema.sql` |
| **Business Usage** | Change ingestion, candidate selection for RCA, feature engineering |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `change_type` | TEXT | YES | — | CHECK: `code`, `schema`, `config` |
| `description` | TEXT | YES | — | |
| `git_ref` | TEXT | YES | — | |
| `created_at` | TIMESTAMP | NOT NULL | `NOW()` | |
| `created_by` | TEXT | YES | — | |
| `modified_at` | TIMESTAMP | YES | — | |
| `modified_by` | TEXT | YES | — | |

**Primary Key:** `id`  
**Foreign Keys:** None  
**Referenced By:** `change_impacts`, `root_cause_hypotheses`, `incident_change_features`

---

### 6. `change_impacts`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Maps a change to impacted entities with severity level |
| **Defined in** | `initial_schema.sql` |
| **Business Usage** | Direct impact recording, BFS propagation, correlation scoring |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `change_id` | UUID | YES | — | FK → `changes(id)` ON DELETE CASCADE |
| `entity_type` | TEXT | YES | — | CHECK: `service`, `api`, `db_table` |
| `entity_id` | UUID | NOT NULL | — | Polymorphic FK |
| `impact_level` | TEXT | YES | — | CHECK: `low`, `medium`, `high` |
| `created_at` | TIMESTAMP | NOT NULL | `NOW()` | |

**Primary Key:** `id`  
**Foreign Keys:** `change_id` → `changes(id)` ON DELETE CASCADE

---

### 7. `incidents`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Incident records for reliability events |
| **Defined in** | `initial_schema.sql` |
| **Business Usage** | Incident ingestion, RCA pipeline anchor entity |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `title` | TEXT | NOT NULL | — | |
| `severity` | TEXT | YES | — | CHECK: `low`, `medium`, `high`, `critical` |
| `started_at` | TIMESTAMP | NOT NULL | — | |
| `resolved_at` | TIMESTAMP | YES | — | |
| `created_at` | TIMESTAMP | NOT NULL | `NOW()` | |
| `created_by` | TEXT | YES | — | |
| `modified_at` | TIMESTAMP | YES | — | |
| `modified_by` | TEXT | YES | — | |

**Primary Key:** `id`  
**Foreign Keys:** None  
**Referenced By:** `incident_entities`, `root_cause_hypotheses`, `evidence`, `incident_change_features`

---

### 8. `incident_entities`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Affected entities linked to an incident |
| **Defined in** | `initial_schema.sql` |
| **Business Usage** | Defines directly affected services for correlation and feature building |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `incident_id` | UUID | YES | — | FK → `incidents(id)` ON DELETE CASCADE |
| `entity_type` | TEXT | YES | — | CHECK: `service`, `api`, `db_table` |
| `entity_id` | UUID | NOT NULL | — | Polymorphic FK |

**Primary Key:** `id`  
**Foreign Keys:** `incident_id` → `incidents(id)` ON DELETE CASCADE

---

### 9. `root_cause_hypotheses`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Ranked root-cause hypotheses linking incidents to likely contributing changes |
| **Defined in** | `initial_schema.sql` + `ALTER TABLE` in same file |
| **Business Usage** | Rule-based correlation output, hybrid scoring input, evidence linking |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `incident_id` | UUID | YES | — | FK → `incidents(id)` ON DELETE CASCADE |
| `description` | TEXT | NOT NULL | — | |
| `confidence` | FLOAT | YES | — | CHECK: 0–1 |
| `created_at` | TIMESTAMP | NOT NULL | `NOW()` | |
| `created_by` | TEXT | YES | — | |
| `modified_at` | TIMESTAMP | YES | — | |
| `modified_by` | TEXT | YES | — | |
| `change_id` | UUID | YES | — | Added via ALTER; **no FK constraint** |

**Primary Key:** `id`  
**Foreign Keys:** `incident_id` → `incidents(id)` ON DELETE CASCADE  
**Logical Dependencies:** `change_id` → `changes(id)`

---

### 10. `evidence`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Supporting evidence for incidents (logs, metrics, traces, changes) |
| **Defined in** | `initial_schema.sql` |
| **Business Usage** | Evidence linking from hypotheses, explanation context |

**Columns:**

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `incident_id` | UUID | YES | — | FK → `incidents(id)` ON DELETE CASCADE |
| `source_type` | TEXT | YES | — | CHECK: `log`, `metric`, `trace`, `change` |
| `reference` | TEXT | NOT NULL | — | |
| `created_at` | TIMESTAMP | NOT NULL | `NOW()` | |
| `created_by` | TEXT | YES | — | |

**Primary Key:** `id`  
**Foreign Keys:** `incident_id` → `incidents(id)` ON DELETE CASCADE

---

### 11. `incident_change_features`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | ML feature store — incident/change pair features for training and hybrid RCA scoring |
| **Defined in** | `add_feature_columns.sql` (authoritative after migration order) |
| **Business Usage** | Feature builder, model training, hybrid predictor |

**Effective Schema** (matches application code):

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | NOT NULL | `uuid_generate_v4()` | PK |
| `incident_id` | UUID | YES | — | Logical FK → `incidents` |
| `change_id` | UUID | YES | — | Logical FK → `changes` |
| `temporal_proximity` | FLOAT | YES | — | 0–1 proximity score |
| `service_overlap` | FLOAT | YES | — | Overlap count with affected services |
| `graph_distance` | FLOAT | YES | — | 0=direct, 1=indirect, 2=weak |
| `criticality_score` | FLOAT | YES | — | Max criticality of impacted services |
| `label` | INTEGER | YES | — | Training label (0/1) |
| `created_at` | TIMESTAMP | YES | `NOW()` | |

**Primary Key:** `id`  
**Foreign Keys:** None declared

**Stale Alternate Definition** in `incident_change_features.sql` (never applied on fresh install):

| Column | Type |
|--------|------|
| `impact_score` | FLOAT |
| `graph_distance` | INT |
| `time_delta_hours` | FLOAT |
| `evidence_count` | INT |
| `label` | INT |

---

## Views

**None found.**

---

## Materialized Views

**None found.**

---

## Sequences

**None explicitly defined.** UUID generation uses `uuid-ossp` extension function `uuid_generate_v4()`.

---

## Triggers

**None found.**

---

## Functions

**None user-defined.** Only PostgreSQL/extension builtins:

- `uuid_generate_v4()` (from `uuid-ossp`)
- `NOW()`

---

## Stored Procedures

**None found.** All business logic resides in Python application code.

---

## Indexes

**No explicit `CREATE INDEX` statements.**

Implicit indexes from constraints:

| Object | Index Type | Column(s) |
|--------|------------|-----------|
| All 11 tables | PRIMARY KEY (B-tree) | `id` |
| `services` | UNIQUE (B-tree) | `name` |

---

## Constraints (Complete Inventory)

### Primary Keys (11)

All tables: `PRIMARY KEY (id)`

### Foreign Keys (5 explicit)

| Table | Column | References | On Delete |
|-------|--------|------------|-----------|
| `apis` | `service_id` | `services(id)` | CASCADE |
| `change_impacts` | `change_id` | `changes(id)` | CASCADE |
| `incident_entities` | `incident_id` | `incidents(id)` | CASCADE |
| `root_cause_hypotheses` | `incident_id` | `incidents(id)` | CASCADE |
| `evidence` | `incident_id` | `incidents(id)` | CASCADE |

### Unique Constraints (1)

- `services.name` — UNIQUE

### CHECK Constraints

| Table | Column | Allowed Values |
|-------|--------|----------------|
| `services` | `criticality` | `low`, `medium`, `high` |
| `dependencies` | `source_type` | `service`, `api` |
| `dependencies` | `target_type` | `service`, `db_table` |
| `changes` | `change_type` | `code`, `schema`, `config` |
| `change_impacts` | `entity_type` | `service`, `api`, `db_table` |
| `change_impacts` | `impact_level` | `low`, `medium`, `high` |
| `incidents` | `severity` | `low`, `medium`, `high`, `critical` |
| `incident_entities` | `entity_type` | `service`, `api`, `db_table` |
| `root_cause_hypotheses` | `confidence` | `>= 0 AND <= 1` |
| `evidence` | `source_type` | `log`, `metric`, `trace`, `change` |

### Logical / Application-Level Relationships (no DDL FK)

```
dependencies.source_id          → services | apis
dependencies.target_id          → services | db_tables
change_impacts.entity_id        → services | apis | db_tables
incident_entities.entity_id     → services | apis | db_tables
root_cause_hypotheses.change_id → changes
incident_change_features.*      → incidents, changes
```
