# E-Voting Refactored Project — Structure

This document describes the entire layout and design of the refactored E-Voting console application.

---

## 1. Folder Tree

```
refactored/
├── README.md                 # How to run, design summary, report
├── STRUCTURE.md              # This file: full structure reference
├── e_voting_console_app.py   # Entry point: load data, login loop, dispatch to dashboards
├── ui/                       # UI layer
│   ├── __init__.py
│   ├── themes.py             # ANSI colors and theme constants (THEME_LOGIN, THEME_ADMIN, …)
│   └── console.py            # Headers, menus, prompts, messages, clear_screen, pause, masked_input
├── models/                   # Domain constants
│   ├── __init__.py
│   └── constants.py          # MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, REQUIRED_EDUCATION_LEVELS, MIN_VOTER_AGE
├── data/                     # Data layer
│   ├── __init__.py
│   ├── store.py              # DataStore: in-memory dicts + load/save evoting_data.json
│   ├── repository.py         # Repositories: Candidate, Station, Position, Poll, Voter, Admin, Vote, Audit
│   └── context.py            # DataContext: single object holding store + all repositories
├── services/                 # Business logic (no UI)
│   ├── __init__.py
│   ├── auth_service.py       # login_admin, login_voter, session (current_user, current_role)
│   ├── audit_service.py      # log_action
│   ├── candidate_service.py  # create, get_all, get_by_id, update, can_delete, deactivate, search_*
│   ├── station_service.py    # create, get_all, get_by_id, update, count_voters_at_station, deactivate
│   ├── position_service.py   # create, get_all, get_by_id, update, can_delete, deactivate
│   ├── poll_service.py      # create, get_all, get_by_id, update, delete, open_poll, close_poll, reopen_poll, assign_candidates
│   ├── voter_service.py      # register, get_all, get_by_id, verify, verify_all, deactivate, search_*, update_password
│   ├── admin_service.py      # can_create_admin, can_deactivate_admin, create_admin, get_all, get_by_id, deactivate
│   └── voting_service.py     # get_open_polls, get_open_polls_for_voter, cast_vote, get_voting_history, get_poll_results, get_station_wise_results
└── app/                      # Application / orchestration
    ├── __init__.py
    ├── login_flow.py         # Main login menu, admin/voter login, voter registration, exit
    ├── admin_dashboard.py    # Admin menu loop + all 30 admin handlers (CRUD, results, audit)
    └── voter_dashboard.py    # Voter menu loop + vote, history, results, profile, change password
```

---

## 2. Role of Each Package

| Package   | Responsibility |
|----------|----------------|
| **ui**   | Console presentation only: colors, headers, menus, prompts, success/error/info messages, clear_screen, pause, masked_input. No business rules, no file paths, no data access. |
| **models** | Domain constants used by services (age limits, education levels). No behavior. |
| **data** | Persistence and access: **store** loads/saves `evoting_data.json` and holds all in-memory dicts; **repository** wraps the store with get/add/list/remove per entity; **context** is the single object (store + repos) passed into services. |
| **services** | All business logic: validation, eligibility, CRUD rules, voting and tallying. They take `DataContext` and (where needed) session; they return data or (success, message). They do not print or read input. |
| **app**  | Orchestration: login flow and admin/voter dashboard loops. They call **ui** for all I/O and **services** for all logic; they do not access the store directly except through services. |

---

## 3. How the Layers Connect

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  e_voting_console_app.py (entry point)                          │
  │  Creates DataContext, loads store, runs login loop; on login    │
  │  calls admin_dashboard(ctx) or voter_dashboard(ctx).            │
  └───────────────────────────────┬─────────────────────────────────┘
                                  │
  ┌───────────────────────────────▼─────────────────────────────────┐
  │  app/ (login_flow, admin_dashboard, voter_dashboard)             │
  │  Menus and prompts via ui; all actions via services; session    │
  │  from auth_service.                                             │
  └───────────────┬─────────────────────────────┬───────────────────┘
                  │                             │
  ┌───────────────▼──────────┐    ┌──────────────▼───────────────────┐
  │  ui/ (console, themes)  │    │  services/ (auth, audit,         │
  │  All user I/O           │    │  candidate, station, position,   │
  │                         │    │  poll, voter, admin, voting)      │
  └─────────────────────────┘    └──────────────┬────────────────────┘
                                               │
                                ┌──────────────▼────────────────────┐
                                │  data/ (DataContext → store +      │
                                │  repositories)                     │
                                │  Persistence and entity access     │
                                └───────────────────────────────────┘
```

- **UI** is used only by **app**.
- **App** uses **services** for every action; it never touches the store or repositories directly.
- **Services** use **DataContext** (store + repositories) and (for session) **auth_service**; they never import **ui** or **app**.

---

## 4. Repository Pattern (store vs repository)

- **store.py**  
  - Owns the JSON file path and the in-memory dicts/lists (candidates, voting_stations, polls, positions, voters, admins, votes, audit_log) and ID counters.  
  - Methods: `load()`, `save()`, and `_ensure_default_admin()`.  
  - Callers do not use the store directly; they use **repositories**.

- **repository.py**  
  - One class per entity (e.g. `CandidateRepository`, `VoterRepository`). Each holds a reference to the store and exposes a small API:  
    - `get_all()`, `get_by_id(id)`, `add(id, data)` and, where needed, `next_id()`, `remove(id)`, `remove_by_poll_id(id)`, etc.  
  - Services receive **DataContext**, which holds the store and all repositories. So services call e.g. `ctx.candidates.add(cid, data)` or `ctx.votes.append(vote)` instead of touching `store.candidates` or `store.votes` directly.  
  - This keeps persistence and structure of storage behind a single layer and makes it easier to change storage later (e.g. another file or database) by changing only the data layer.

- **context.py**  
  - Builds one **DataStore** and one of each repository (Candidate, Station, Position, Poll, Voter, Admin, Vote, Audit) and exposes them as attributes of **DataContext**. The entry point creates one `DataContext`, loads the store, and passes this context into the app and thus into all services.

---

## 5. Entry Point and Data File

- **Entry point:** `e_voting_console_app.py`.  
  - Adds the `refactored` directory to `sys.path` so that imports like `ui`, `services`, `data`, `app`, `models` resolve.  
  - Sets the process current working directory to the `refactored` directory so that `evoting_data.json` is read/written there.  
  - Creates a **DataContext**, calls `ctx.store.load()`, then runs the main loop: `run_login(ctx)` → if logged in, `run_admin_dashboard(ctx)` or `run_voter_dashboard(ctx)` → on logout, `auth_service.clear_session()` and loop again; if user chose Exit, loop exits and the program ends.

- **Data file:** `evoting_data.json` is created and updated in the **refactored** directory (same directory as `e_voting_console_app.py`).  
  - Run from the refactored folder: `python e_voting_console_app.py` (or `python -m e_voting_console_app` with appropriate path).  
  - Default admin (username `admin`, password `admin123`) is ensured on first load if no file exists.

---

## 6. Behaviour Parity

The refactored application preserves the same menus, prompts, and outputs as the original single-file monolith. No new features were added. All original flows (admin and voter CRUD, voting, results, audit) are implemented via the layers above so that behaviour remains identical while the code is modular, object-oriented, and separated by concerns.
