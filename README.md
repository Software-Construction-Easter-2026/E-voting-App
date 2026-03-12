# GROUP MEMBERS

* 1. TEDNO CALVIN S23B23/013
* 2. ANGUYI NEWTON S23B23/071
* 3. OPIFUDRIRA TIMOTHY S23B23/086
* 4. 
* 5. 
* 6.  

# National E-Voting Console Application (Refactored)

A modular, object-oriented refactor of the original single-file National E-Voting console application. Behaviour is unchanged: same menus, prompts, and outputs. No new features have been added.

## How to Run

From the project root:

```bash
python main.py
```

Default admin login: **username** `admin`, **password** `admin123`.

On Windows, if the console reports an encoding error on the menu borders, run with UTF-8 (e.g. `set PYTHONIOENCODING=utf-8` or `chcp 65001` in the terminal first).

---

## System Architecture

The application is split into four layers:

```
┌─────────────────────────────────────────────────────────────────┐
│  Presentation (UI)                                               │
│  menus/login_menu, admin_menu, voter_menu, admin_handlers*,      │
│  ui/display, ui/console_io, core/colors                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│  Application / Services (Business logic)                         │
│  auth, candidate, station, position, poll, voter, admin,         │
│  vote, audit, results                                           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│  Data (Persistence & in-memory state)                            │
│  data/repository                                                │
└─────────────────────────────────────────────────────────────────┘
```

- **UI layer**: Renders headers, menus, messages, and reads user input. No business rules; only calls services and shows results.
- **Service layer**: Encapsulates rules (e.g. candidate eligibility, duplicate vote prevention, poll lifecycle). Uses the repository for all reads/writes.
- **Data layer**: Single `Repository` class holding in-memory dicts and counters, plus `save()` / `load()` to JSON. No UI or business logic.

---

## Project Structure

```
E-voting-App/
├── main.py                    # Entry point: wiring, load data, login loop
├── e_voting_console_app.py    # Original monolith (unchanged)
├── evoting_data.json          # Created at runtime (persisted data)
├── README.md
└── evoting/
    ├── __init__.py
    ├── app_context.py         # Holds repo + all services for menus
    ├── core/
    │   ├── constants.py       # MIN/MAX ages, education levels, data file name
    │   └── colors.py          # ANSI colour constants and themes
    ├── data/
    │   └── repository.py      # In-memory store + JSON load/save
    ├── services/
    │   ├── audit_service.py   # Append to audit log
    │   ├── auth_service.py    # Login (admin/voter), registration, session
    │   ├── candidate_service.py
    │   ├── station_service.py
    │   ├── position_service.py
    │   ├── poll_service.py
    │   ├── voter_service.py   # Admin-side voter ops
    │   ├── admin_service.py
    │   ├── vote_service.py    # Cast vote, duplicate prevention
    │   └── results_service.py # Tally, stats, station-wise results
    ├── ui/
    │   ├── console_io.py      # clear_screen, pause, prompt, masked_input
    │   └── display.py        # header, subheader, error, success, table, etc.
    └── menus/
        ├── login_menu.py      # Login / register / exit
        ├── admin_menu.py      # Admin dashboard and dispatch
        ├── admin_handlers.py  # Candidate, station, position, poll handlers
        └── admin_handlers_extra.py  # Voter, admin, results, audit handlers
        └── voter_menu.py      # Voter dashboard and all voter flows
```

---

## Design Decisions

### 1. Modular design and single responsibility

- **Core**: Constants and colours live in `core/` so they can be shared without pulling in UI or data.
- **Data**: One `Repository` owns all entities and persistence. No other module touches JSON or global dicts.
- **Services**: One service per domain (candidates, stations, positions, polls, voters, admins, votes, audit, results). Each has a clear responsibility and uses the repository only.

### 2. Object-oriented design and encapsulation

- **Repository**: Holds candidates, stations, polls, positions, voters, admins, votes, audit log, and ID counters. Exposes them as attributes; `save()` and `load()` hide JSON details.
- **Services**: Take `Repository` (and where needed `AuditService` or `AuthService`) in the constructor. Business rules (e.g. age limits, criminal record, “already voted”) live inside services, not in UI or repository.
- **AppContext**: Injects the single repository and all services into menus so handlers stay thin and only do UI + one or two service calls.

### 3. Separation of concerns

- **UI vs logic**: Menus and handlers only format output and read input; they call services and show success/error messages. They do not compute eligibility, update state, or persist.
- **Logic vs data**: Services never print or read from the console. They return success/failure and data; the UI layer decides what to show (e.g. “Candidate must be at least 25 years old. Current age: 22”).
- **Data**: Repository does not know about prompts, colours, or business rules; it only stores and loads structured data.

### 4. Clean code

- **Naming**: Service methods are verb-based (`create`, `update`, `deactivate`, `get_all`, `search_by_name`). Menu handlers are named by action (`create_candidate`, `view_all_voters`).
- **No duplication**: Shared behaviour (e.g. “can this candidate be deactivated?”) is in the service (e.g. `can_deactivate`); UI only calls it and displays the result.
- **Readability**: Long flows (e.g. admin dashboard) are split into small handler functions; the dashboard file only lists menu options and maps choices to handlers.

### 5. Behaviour preserved

- All original menus, options, and prompts are unchanged.
- Same validation (age, education, criminal record for candidates; station and verification for voters; poll status for open/close/assign).
- Same outputs (tables, bar charts, turnout, station-wise results, audit log).
- Data file remains `evoting_data.json`; format is compatible so existing data can be used with the refactored app.

---

## Feature Summary (Unchanged)

- **Candidate CRUD**: Age (25–75), education level, no criminal record.
- **Voting stations**: CRUD and capacity.
- **Positions and polls**: Create/update/delete; assign candidates; open/close; draft → open → closed.
- **Voters**: Registration at a station; admin verification; view/verify/deactivate/search.
- **Admins**: Four roles (super_admin, election_officer, station_manager, auditor); only super_admin creates/deactivates admins.
- **Voting**: One vote per voter per poll; duplicate prevention; abstain option; vote hash reference.
- **Results**: Per-position bar charts, turnout, station-wise results, detailed statistics, audit log.

---

