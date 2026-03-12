# GROUP MEMBERS
# 1. NABASA ISAAC         M23B23/043
# 2. LAKICA LETICIA       M23B23/023
# 3. ATWIJUKRIE APOPHIA   M23B2/051


# National E-Voting Console Application (Refactored)

**Software Construction — Year 3, Semester 2 — Easter 2026 Semester Test**  
Uganda Christian University | Department of Computing & Technology

This project is a refactored version of the original single-file E-Voting console application. Behaviour is **identical** to the original (same menus, prompts, and outputs). No new features were added.

---

## How to Run

From the project root:

```bash
python main.py
```

Default admin login: **username** `admin`, **password** `admin123`.  
Data is stored in `evoting_data.json` in the same directory.

---

## Design Principles Applied

### 1. Modular Design

The monolith was split into **modules** with clear boundaries:

- **`src/config/`** — Constants (ANSI colours, business rules, file path). One place for magic numbers and theme.
- **`src/data/`** — Data layer: `Repository` holds all in-memory state and handles load/save to JSON.
- **`src/models/`** — Placeholder for domain concepts; entities are still dict-based for JSON compatibility.
- **`src/ui/`** — Console I/O only: colours, headers, prompts, tables, clear screen, pause. No business logic.
- **`src/services/`** — Business logic: auth, candidates, stations, positions, polls, voters, admins, voting, results, audit. No printing or input.
- **`src/menus/`** — Controllers: present menus, read user input, call services, show results. Tie UI and logic together.

Each module has a **single responsibility** and can be tested or changed with minimal impact on others.

### 2. Object-Oriented Design

- **`Repository`** (in `src/data/repository.py`): Encapsulates all application data (candidates, voters, polls, votes, etc.) and IDs. Replaces the original global dicts and counters. Exposes `load()`, `save()`, and the data structures.
- **Session**: Login returns a session object `{"user": ..., "role": "admin"|"voter"}` passed into dashboards. No global `current_user`/`current_role`.
- **Inheritance**:  
  - **`BaseMenu`** (`src/menus/base_menu.py`): Abstract base for all menu controllers. Holds `repo` and `ui` (console), and provides helpers (`clear_screen`, `pause`, `prompt`, `success`, `error`, etc.).  
  - **`AdminHandlerBase(BaseMenu)`** (`src/menus/admin_handlers/base.py`): Extends `BaseMenu` with `session`, `user`, and an `AuditService` instance. All admin section handlers inherit from this.  
  - **`LoginMenu(BaseMenu)`**, **`AdminMenu(BaseMenu)`**: Login and admin entry points; admin menu composes handler instances (see below).
- **Composition**: **`AdminMenu`** does not implement the 32 actions itself. It composes instances of seven handler classes: `AdminCandidateHandlers`, `AdminStationHandlers`, `AdminPositionHandlers`, `AdminPollHandlers`, `AdminVoterHandlers`, `AdminAccountHandlers`, `AdminResultsHandlers`. Each handler owns one section of the admin dashboard (e.g. candidate CRUD, poll lifecycle, results/audit). This keeps each file under ~250 lines and gives a single responsibility per handler.
- **Class-based services**: **`BaseService`** (`src/services/base_service.py`) is the common base for business-logic classes; it holds a `Repository` reference. **`AuthService`**, **`AuditService`**, and **`CandidateService`** extend `BaseService` and encapsulate auth, audit logging, and candidate operations. Other services remain module-level functions that take `repo` for gradual migration.

### 3. Separation of Concerns

- **Data layer** (`Repository`): Load/save and in-memory state. No UI, no business rules.
- **Logic layer** (services): Validation, eligibility, CRUD, tallying. No `print` or `input`; they return values for the caller to use.
- **UI layer** (`src/ui/console.py`): How things look and how input is read. No knowledge of candidates, polls, or votes.
- **Presentation/controller layer** (menus): Decide what to show and what to ask; call services and repository; display results via the UI module.

This keeps display, business rules, and storage **fully decoupled**.

### 4. Clean Code

- **Naming**: Descriptive names (`run_admin_dashboard`, `_create_candidate`, `get_poll_results`, `try_admin_login`).
- **Readability**: Short functions, clear control flow, minimal duplication.
- **Comments**: Human-readable comments in key modules (e.g. docstrings for modules and main functions, inline notes where logic is non-obvious).
- **No duplication**: Shared behaviour (e.g. status badges, table headers, prompts) lives in `console.py` or in services; menus only orchestrate.

---

## Project Structure

```
E-voting-App/
├── main.py                 # Entry point: load repo, run login loop, dispatch to admin/voter dashboard
├── e_voting_console_app.py # Original monolith (kept for reference)
├── evoting_data.json       # Created at runtime; persists all data
├── README.md               # This file
└── src/
    ├── __init__.py
    ├── config/
    │   ├── __init__.py
    │   └── constants.py    # Colours, MIN/MAX ages, education levels, data file path
    ├── data/
    │   ├── __init__.py
    │   └── repository.py   # Repository class: state + load/save
    ├── models/
    │   └── __init__.py     # Domain placeholders (entities as dicts)
    ├── ui/
    │   ├── __init__.py
    │   └── console.py      # Headers, prompts, colours, tables, clear, pause
    ├── services/
    │   ├── __init__.py
    │   ├── auth_service.py      # Login (admin/voter), voter registration
    │   ├── audit_service.py    # Log action, get/filter audit entries
    │   ├── candidate_service.py # Candidate CRUD and search
    │   ├── station_service.py   # Station CRUD, count voters per station
    │   ├── position_service.py  # Position CRUD
    │   ├── poll_service.py      # Poll CRUD, open/close/reopen, assign candidates
    │   ├── voter_service.py     # Verify, deactivate, search voters
    │   ├── admin_service.py     # Create/deactivate admin accounts
    │   ├── voting_service.py    # Cast vote, change password, helpers for voter
    │   └── results_service.py   # Poll results, detailed stats, station-wise results
    └── menus/
        ├── __init__.py
        ├── base_menu.py    # BaseMenu: repo + ui helpers for all menus
        ├── login_menu.py   # LoginMenu(BaseMenu): login screen, registration
        ├── admin_menu.py   # AdminMenu(BaseMenu): 32-option menu, dispatches to handlers
        ├── voter_menu.py   # Voter dashboard and all 7 voter actions
        └── admin_handlers/ # One class per admin section (inherits AdminHandlerBase)
            ├── base.py           # AdminHandlerBase(BaseMenu): session, user, audit
            ├── candidate_handlers.py  # Candidate CRUD + search
            ├── station_handlers.py    # Station CRUD
            ├── position_handlers.py   # Position CRUD
            ├── poll_handlers.py       # Poll CRUD, open/close, assign candidates
            ├── voter_handlers.py      # View/verify/deactivate/search voters
            ├── account_handlers.py    # Create/view/deactivate admins
            └── results_handlers.py   # Poll results, statistics, audit log, station-wise
```

---

## OOP at a glance

- **BaseMenu** → **LoginMenu**, **AdminMenu** (menus get `repo` + `ui`).
- **BaseMenu** → **AdminHandlerBase** (adds `session`, `user`, `audit`) → **AdminCandidateHandlers**, **AdminStationHandlers**, **AdminPositionHandlers**, **AdminPollHandlers**, **AdminVoterHandlers**, **AdminAccountHandlers**, **AdminResultsHandlers**.
- **AdminMenu** *has-a* instance of each of the seven handler classes and delegates menu choices to them (composition).
- **BaseService** → **AuthService**, **AuditService**, **CandidateService** (business logic with shared `repo`).

No single file (e.g. admin logic) exceeds ~250 lines; responsibilities are split by class and file.

---

## Summary

The refactor keeps **all original behaviour** while improving structure: logical file separation, a single `Repository` for data, class-based and function-based services for logic, and a thin UI plus menu layer. The admin dashboard uses **inheritance** (BaseMenu → AdminHandlerBase → section handlers) and **composition** (AdminMenu composes seven handler instances). The result is easier to maintain, test, and extend without changing the user-facing flow.
