# Template guide

[Back to README](../README.md) · [Architecture](architecture.md)

A **template** is a pair of config files, `roles.yaml` and `schema.yaml`, plus the data they describe (a SQLite database, documents and optional memory). Switching templates needs no code changes.

## 1. Pick a config directory

```
backend/templates/helpdesk/
├── roles.yaml
├── schema.yaml
└── data/            # your db, docs/, memory.json (any location works)
```

Start from the demo files (`backend/roles.yaml`, `backend/schema.yaml`) and edit. Point the app at your directory with `CRM_CONFIG_DIR`; it defaults to `backend/`.

## 2. Describe your data in `schema.yaml`

```yaml
db: templates/helpdesk/data/helpdesk.db
docs_dir: templates/helpdesk/data/docs
memory_file: templates/helpdesk/data/memory.json
vectorstore: templates/helpdesk/vectorstore
user_table: {name: agents, id: id, display: name, role: role}
owner_columns: {cases: assigned_agent}
```

| Key | Meaning |
|---|---|
| `db`, `docs_dir`, `memory_file`, `vectorstore` | Paths, relative to `backend/` |
| `user_table` | Table of people who can ask: its name, id column, display-name column and the column holding their role |
| `owner_columns` | Per table, the column holding the owning user's id. Used when a role has `row_scope: own` |

## 3. Define roles in `roles.yaml`

```yaml
agent:
  sql:
    cases: [id, assigned_agent, status, summary]
    customers: [id, name, plan]
  row_scope: own          # own | all
  doc_tags: [kb]
  memory: own             # own | team | none

manager:
  sql:
    cases: [id, assigned_agent, status, summary]
    customers: [id, name, plan, revenue]
    agents: [id, name, role]
  row_scope: all
  doc_tags: [kb, policy]
  memory: team
```

Rules:

- Role names are free-form, but each must match the values in your `user_table` role column exactly.
- List every column a role may read. Anything not listed is invisible to that role.
- A role with an empty `doc_tags: []` skips the vector store; `memory: none` skips memory.
- List the id column first for each table; source labels like `sql:cases#12` use the first column.

## 4. Add your data

- **Database:** create the SQLite file at the `db` path with the tables and columns your config names. `scripts/seed_db.py` is demo-specific; write your own loader or import script.
- **Documents:** put `.txt` files in `docs_dir`, named `<tag>_<anything>.txt`. The prefix before the first underscore is the doc tag (`kb_refunds.txt` has tag `kb`). Roles see a document only if its tag is in their `doc_tags`.
- **Memory (optional):** a JSON list of `{"user_id": 1, "text": "..."}`.

## 5. Build and run

```bash
export CRM_CONFIG_DIR=$PWD/backend/templates/helpdesk
python scripts/ingest.py
cd backend && uvicorn main:app
streamlit run frontend/app.py          # from the repo root, in another terminal
```

Re-run `ingest.py` whenever you change documents or any role's `doc_tags`.

## Checklist before trusting a new template

- Ask the same question as each role and confirm the sources and answer differ as intended.
- Confirm a role with `row_scope: own` cannot see other users' rows.
- Confirm hidden columns (such as notes or revenue) never appear in sources.
- `backend/test_router.py` shows how to assert these boundaries; copy its pattern for your roles.

## Current limits

- Documents must be `.txt`.
- Retrieval always queries every source a role is allowed. There is no per-query source selection.
- Authentication is out of scope; see the note in [Architecture](architecture.md#security-notes).
