# National E-Voting System — Refactoring Report

**Course:** Software Construction · **Program:** BsCS Year 3,2 · **Semester:** Easter 2026

---

## 1. Original Problem

The original application (`e_voting_console_app.py`, ~1 633 lines) was a single-file monolith. All UI rendering, business logic, data storage, authentication, and CRUD operations were packed into one file using global variables and procedural functions. This violated modular design, separation of concerns, and made the codebase difficult to maintain, test, or extend.

## 2. Initial Audit & Task Allocation

Before restructuring the application, the team conducted a comprehensive review of the monolith—documented in `Audit.md`. We mapped out the required components and distributed responsibilities to allow parallel development with minimal merge conflicts. 

Prioritization was structured specifically around **collaboration and extensibility**:
1. **Foundation First:** Carol built the shared UI utilities (`ui.py`, `colors.py`), global settings/auth (`auth_service.py`), and the decoupled data layer (`api_engine.py`). This provided a stable API for everyone else to build upon.
2. **Independent Domains:** The business logic was logically partitioned, allowing developers to work on separate modules that relied solely on the shared `DatabaseEngine`:
   - **Carol:** Admin Dashboard and Authentication logic.
   - **Ezra:** Candidate, Station, and Position Management CRUD.
   - **Charis:** Poll Management, Voter Management, and Admin Management.
   - **Nathaniel:** The Voting Process (Voter Dashboard), Stats & Results generation, and main app integration.

Because UI rendering and data persistence were fully abstracted early on, team members could work simultaneously without interfering with each other's code.

## 3. Refactored Project Structure

```
E-Voting-App/
├── database.json                 ← Single JSON file acting as the database
├── Frontend/
│   ├── main.py                   ← Entry point: login routing
│   ├── api_engine.py             ← Database engine (data access layer)
│   ├── auth_service.py           ← Authentication & voter registration
│   ├── admin_dashboard.py        ← All 32 admin menu options & CRUD
│   ├── voter_dashboard.py        ← Voter-facing features (7 options)
│   ├── stats_results.py          ← Poll results, statistics, audit log
│   ├── ui.py                     ← Shared UI helpers (header, prompt, etc.)
│   ├── colors.py                 ← ANSI colour codes & theme constants
│   └── security.py               ← Password hashing utility
└── Backend/
    ├── storage.py                ← Generic JsonStore class
    ├── audits.py                 ← Audit log operations
    ├── voters_management.py      ← Voter verification, search, deactivation
    ├── candidate_management/     ← Candidate CRUD operations
    ├── station_management.py     ← Station CRUD operations
    ├── position_management.py    ← Position CRUD operations
    ├── polls_management.py       ← Poll lifecycle management
    └── admin_management.py       ← Admin account management
```

## 4. Design Decisions

### Modular Design (25%)

The monolith was split by **responsibility**. Each file handles one clearly defined area:

| Module | Responsibility |
|--------|---------------|
| `api_engine.py` | All reads/writes to `database.json` |
| `auth_service.py` | Admin login, voter login, voter registration |
| `admin_dashboard.py` | Admin menu routing + candidate/station/position/poll/voter/admin CRUD |
| `voter_dashboard.py` | Voter menu routing + cast vote, view polls, history, profile |
| `stats_results.py` | Poll results, detailed statistics, station-wise results, audit log |
| `ui.py` | Terminal rendering (headers, prompts, tables, colours) |

No module exceeds a single, well-defined concern.

### Object-Oriented Design (20%)

The **`DatabaseEngine`** class in `api_engine.py` encapsulates all data access. It treats `database.json` top-level keys as logical "tables" and exposes CRUD methods:

- **Dict-tables** (candidates, voters, polls, etc.): `get_all()`, `get_by_id()`, `find()`, `insert()`, `update()`, `delete()`
- **List-tables** (votes, audit_log): `get_list()`, `append_to_list()`, `filter_list()`, `replace_list()`
- **Counters**: `get_next_id()`, `increment_counter()` — auto-incrementing IDs per table
- **Audit convenience**: `log_action()` — appends timestamped entries to the audit log

Internal data (`self._data`) is private. No other module reads or writes JSON files directly.

### Separation of Concerns (20%)

The architecture enforces a **three-layer separation**:

```
┌─────────────────────────────────────────────┐
│  UI Layer        ui.py, colors.py           │  ← Rendering only
├─────────────────────────────────────────────┤
│  Logic Layer     admin_dashboard.py          │
│                  voter_dashboard.py           │  ← Business rules
│                  auth_service.py              │
│                  stats_results.py             │
├─────────────────────────────────────────────┤
│  Data Layer      api_engine.py               │  ← Storage only
│                  database.json                │
└─────────────────────────────────────────────┘
```

- **UI layer** — `ui.py` contains only display functions (`header()`, `prompt()`, `menu_item()`, `masked_input()`). It knows nothing about data or business rules.
- **Logic layer** — Each dashboard module calls UI functions for display and `DatabaseEngine` methods for data. It never touches the filesystem.
- **Data layer** — `DatabaseEngine` is the sole gateway to `database.json`. Every `insert()`, `update()`, and `delete()` immediately persists to disk.

### Clean Code Quality (15%)

- **Naming:** Functions like `create_candidate()`, `view_poll_results()`, and `cast_vote()` clearly state their intent.
- **No duplication:** Shared UI helpers (`header()`, `prompt()`, `status_badge()`, etc.) are defined once in `ui.py` and imported everywhere.
- **Small functions:** Each admin CRUD operation is its own standalone function with a single task.
- **Consistent style:** All modules follow the same pattern: import UI helpers → import colours → define functions that take `(db, current_user)`.
- **No global state:** The original used 15+ global variables (`candidates`, `voters`, `current_user`, etc.). The refactored version passes `db` and `current_user` as explicit parameters.

### Working Application (10%)

The refactored application behaves **identically** to the original:

- Same 4-option login menu (admin, voter, register, exit)
- Same 32-option admin dashboard with the same section groupings
- Same 7-option voter dashboard
- Same prompts, same validation messages, same output formatting
- Same password masking with `*` characters
- Same ANSI colour theme throughout

**To run:** `cd Frontend && python3 main.py`

## 5. How the Database Engine Works

Instead of loading the entire JSON into scattered global dictionaries, all data flows through one `DatabaseEngine` instance:

```python
db = DatabaseEngine("database.json")
db.load()                                    # Load once at startup
voters = db.get_all("voters")                # Read a "table"
db.insert("voters", next_id, voter_record)   # Insert a record
db.update("voters", vid, {"is_verified": True})  # Partial update
db.log_action("VERIFY_VOTER", admin, details)    # Audit logging
```

This enforces that **no business logic function ever calls `open()` or `json.dump()`** — all persistence is handled by the engine.

---

*Refactored by the project team as part of the Easter 2026 Software Construction examination.*
