# National E-Voting System — Refactored

**Course:** BsCS Software Construction, Year 3.2, Easter 2026 Semester  
**University:** Uganda Christian University  
**Task:** Refactor a monolithic 1,632-line Python console application into a modular, object-oriented project while preserving identical behaviour.

---

## Table of Contents

1. [What Was Required](#what-was-required)
2. [What Was Implemented](#what-was-implemented)
3. [Project Structure](#project-structure)
4. [Architecture & Design Decisions](#architecture--design-decisions)
5. [SOLID Principles Applied](#solid-principles-applied)
6. [Object-Oriented Design Concepts Applied](#object-oriented-design-concepts-applied)
7. [Other Clean Code & Design Principles Applied](#other-clean-code--design-principles-applied)
8. [What Was Not Done & Why](#what-was-not-done--why)
9. [How to Run](#how-to-run)
10. [Original Features Preserved](#original-features-preserved)
11. [Team Contributions](#team-contributions)

---

## What Was Required

From the exam instructions:

> *"Refactor this monolith into a modular, object-oriented Python project. The application must behave identically after refactoring — same menus, same prompts, same outputs. Do not add new features."*

The four principles to apply:

1. **Modular Design** — Logical file separation, single responsibilities
2. **Object-Oriented Design** — Proper classes, encapsulation, meaningful methods
3. **Separation of Concerns** — UI, logic, and data layers fully decoupled
4. **Clean Code** — Naming, readability, no duplication

Deliverables:

- A GitHub repository with all source files
- A brief report/README.md (1–2 pages) explaining the structure and design decisions

---

## What Was Implemented

### 1. Modular Design (25% weight) — FULLY IMPLEMENTED

The original **1 file with 1,632 lines** and **62 top-level functions** was decomposed into **32 focused source files** organised into a clear package hierarchy:

| Original Problem | Refactored Solution |
|---|---|
| Single file with everything | 5 packages: `models/`, `services/`, `ui/`, `ui/admin/`, and root modules |
| 62 loose functions sharing global state | 8 service classes + 9 UI classes + 7 model classes |
| No logical grouping | Each file has a single, clear responsibility |
| 1,632 lines in one file | Files range from 12–280 lines; the admin dashboard is further split into 6 focused screen modules |

### 2. Object-Oriented Design (20% weight) — FULLY IMPLEMENTED

| Original Problem | Refactored Solution |
|---|---|
| Data stored as plain dictionaries in global variables | 7 model classes with proper encapsulation (`Candidate`, `Voter`, `Admin`, `Poll`, `PollPosition`, `Position`, `Vote`, `VotingStation`) |
| No methods on data — logic scattered across functions | Domain methods on models: `voter.has_voted_in_poll()`, `poll.has_any_candidates()`, `candidate.is_eligible_for_position()`, `poll.open_poll()`, `voter.record_vote()` |
| 14+ global variables for state | Single `DataStore` class encapsulates all state with managed access |
| No serialisation abstraction | Each model provides `to_dict()` / `from_dict()` methods for JSON persistence |
| No constructor injection | All services and UI classes receive dependencies via constructors (Dependency Inversion Principle) |

### 3. Separation of Concerns (20% weight) — FULLY IMPLEMENTED

The monolith mixed input reading, business validation, data mutation, and output formatting in the same functions. The refactored code has three strictly separated layers:

```
┌────────────────────────────────────────────┐
│  UI Layer  (auth_ui, admin_ui, voter_ui)   │  ← Only handles input/output
├────────────────────────────────────────────┤
│  Service Layer  (8 service classes)        │  ← Only handles business logic
├────────────────────────────────────────────┤
│  Data Layer  (DataStore + 7 Model classes) │  ← Only handles persistence & state
└────────────────────────────────────────────┘
```

**Rules enforced:**
- **UI classes** never mutate the DataStore directly — they call services
- **Service classes** never print to the console or read user input
- **Model classes** never call services or perform I/O
- Dependencies flow downward only (UI → Services → Data)

### 4. Clean Code Quality (15% weight) — FULLY IMPLEMENTED

| Practice | What Was Done |
|---|---|
| **Named constants** | All 15+ magic numbers/strings extracted to `constants.py` (e.g., `MIN_CANDIDATE_AGE = 25`, `VOTE_HASH_LENGTH = 16`, `STATION_LOAD_CRITICAL_PERCENT = 100`) |
| **Meaningful names** | Functions like `get_eligible_candidates()`, `calculate_turnout()`, `is_national_id_unique()` instead of vague names |
| **DRY (Don't Repeat Yourself)** | Shared UI formatting centralised in `console.py`; repeated validation extracted into service methods |
| **No mixed responsibilities** | Every function either computes or displays, never both |
| **Docstrings & comments** | Module-level docstrings on all 26 files, class docstrings, method docstrings explaining business intent, section headers for logical groupings |
| **Consistent return conventions** | Services return `(result, None)` on success or `(None, error_message)` on failure throughout |

### 5. Working Application (10% weight) — FULLY IMPLEMENTED

Every original feature was tested and works identically:

- Admin login with default credentials (`admin` / `admin123`)
- Candidate CRUD with age/education eligibility checks
- Voting station management (CRUD + capacity tracking)
- Position creation with level and age requirements
- Full poll lifecycle: create (draft) → assign candidates → open → vote → close → view results
- Voter self-registration with auto-generated card numbers
- Admin voter verification (single and bulk)
- Ballot casting with duplicate prevention and abstention support
- Vote receipt hash generation
- Result tallying with bar charts and turnout percentages
- Voter demographics and station load reports
- Station-wise result breakdowns
- Audit logging with filtering (by action, by user, last N entries)
- JSON data persistence (`evoting_data.json`)
- Role-based admin access (super_admin, election_officer, station_manager, auditor)
- Masked password input with yellow asterisks (cross-platform)
- ANSI-colored console interface with themed screens

### 6. Report (10% weight) — THIS README

---

## Project Structure

```
software-construction/
├── app.py                              # Entry point — wires all layers together
├── e_voting/
│   ├── __init__.py                     # Package docstring
│   ├── constants.py                    # All named constants (replaces magic numbers)
│   ├── store.py                        # Central DataStore — persistence + session
│   ├── models/                         # Domain model classes
│   │   ├── __init__.py                 # Re-exports all models for convenience
│   │   ├── admin.py                    # Admin account entity
│   │   ├── candidate.py                # Election candidate entity
│   │   ├── poll.py                     # Poll + PollPosition (poll lifecycle)
│   │   ├── position.py                 # Elective position entity
│   │   ├── vote.py                     # Individual ballot record
│   │   ├── voter.py                    # Registered voter entity
│   │   └── voting_station.py           # Physical voting station entity
│   ├── services/                       # Business logic layer
│   │   ├── __init__.py                 # Package docstring
│   │   ├── auth_service.py             # Login authentication + voter registration
│   │   ├── candidate_service.py        # Candidate CRUD + search
│   │   ├── station_service.py          # Station CRUD + capacity queries
│   │   ├── poll_service.py             # Poll & position lifecycle management
│   │   ├── voter_service.py            # Admin-side voter management
│   │   ├── admin_service.py            # Admin account management
│   │   ├── vote_service.py             # Ballot casting + receipt generation
│   │   └── result_service.py           # Tallying, statistics, audit log
│   └── ui/                             # Presentation layer
│       ├── __init__.py                 # Package docstring
│       ├── console.py                  # ANSI colors, formatting helpers, input
│       ├── auth_ui.py                  # Login menu + registration screens
│       ├── voter_ui.py                 # Voter dashboard (7 actions)
│       └── admin/                      # Admin dashboard sub-package
│           ├── __init__.py             # Re-exports AdminUI
│           ├── admin_ui.py             # Thin coordinator (~150 lines, menu + dispatch)
│           ├── candidate_screens.py    # CandidateScreens — CRUD + search (~240 lines)
│           ├── station_screens.py      # StationScreens — CRUD (~145 lines)
│           ├── poll_screens.py         # PollScreens — positions + polls (~430 lines)
│           ├── voter_screens.py        # VoterScreens — view, verify, deactivate, search (~140 lines)
│           ├── admin_mgmt_screens.py   # AdminMgmtScreens — create, view, deactivate (~100 lines)
│           └── results_screens.py      # ResultsScreens — results, stats, audit log (~250 lines)
├── e_voting_console_app.py             # Original monolith (kept as reference)
└── README.md                           # This report
```

**32 source files** with clear single responsibilities, compared to the original **1 file** with mixed concerns.

---

## Architecture & Design Decisions

### Why a Three-Layer Architecture?

The exam explicitly required **Separation of Concerns** between UI, logic, and data. A three-layer architecture (Presentation → Business Logic → Data) is the most straightforward way to achieve this while keeping the project simple enough for a console application:

- **UI Layer** (`ui/`): Reads input, displays output, calls services for business operations
- **Service Layer** (`services/`): Enforces all business rules, never prints or reads input
- **Data Layer** (`store.py` + `models/`): Manages persistence and domain state

### Why Constructor-Based Dependency Injection?

All services receive the `DataStore` via their constructor. All UI classes receive their required services via constructors. This follows the **Dependency Inversion Principle** — high-level modules (UI) depend on abstractions (services), not on concrete data manipulation. It also makes the dependency graph explicit in `app.py`.

### Why a Centralised DataStore Instead of Individual Repositories?

The original script used 14+ global variables. A full repository-per-entity pattern would be over-engineered for a JSON-file-based console app. The `DataStore` class strikes a balance: it eliminates global state while keeping the persistence layer simple and matching the original single-file JSON format.

### Why Split admin_ui.py into a Sub-Package?

The admin dashboard has 31 distinct menu actions across 6 categories. Rather than keeping ~1,450 lines in a single file, the admin UI was decomposed into a `ui/admin/` sub-package with 6 focused screen-handler classes (one per category) plus a thin coordinator. Each handler receives only the services it needs (Interface Segregation), and the coordinator maps menu choices to handler methods (Strategy Pattern). This also eliminates merge conflicts when multiple collaborators work on different admin sections.

### Why Regular Classes Instead of Dataclasses?

Dataclasses would reduce boilerplate, but the models need custom `to_dict()`/`from_dict()` methods with `.get()` defaults for backwards-compatible JSON loading. Regular classes with explicit `__init__` make the serialisation logic clearer and avoid hidden magic.

---

## SOLID Principles Applied

### S — Single Responsibility Principle (SRP)

> *"A class should have only one reason to change."*

Every class in the project has exactly one well-defined responsibility:

| Class | Single Responsibility |
|---|---|
| `Candidate` (model) | Represents one candidate's data and eligibility checks |
| `AuthService` | Authenticates users and registers voters — nothing else |
| `CandidateService` | Candidate CRUD and search — nothing else |
| `ResultService` | Calculates tallies, statistics, and reports — nothing else |
| `DataStore` | Manages data collections and JSON persistence — nothing else |
| `AdminUI` | Displays admin screens and collects admin input — nothing else |
| `console.py` | Provides reusable formatting/input helpers — nothing else |

**Before (original monolith):** The function `create_candidate()` read input from the console, validated business rules, mutated global data, printed success/error messages, and saved to disk — five responsibilities in one function.

**After (refactored):** Creating a candidate involves three classes, each doing one thing:
- `AdminUI._create_candidate()` — collects input and displays messages
- `CandidateService.create()` — validates and creates the record
- `DataStore.save()` — persists to JSON

### O — Open/Closed Principle (OCP)

> *"Software entities should be open for extension but closed for modification."*

**1. Strategy pattern in AdminUI dashboard:**
```python
# admin_ui.py — adding a new action only requires one new dict entry + one new method
admin_actions = {
    "1": self._create_candidate,
    "2": self._view_all_candidates,
    ...
    "31": self._save_data,
    # To add action 33: just add "33": self._new_action — no existing code changes
}
```

**2. Backwards-compatible JSON deserialisation:**
```python
# candidate.py — new fields use .get() with defaults, so old JSON files still load
has_criminal_record=data.get("has_criminal_record", False),
years_experience=data.get("years_experience", 0),
```
Adding a new field to a model requires only adding it to `__init__`, `to_dict()`, and `from_dict()` with a default — no changes to `DataStore.save()` or `DataStore.load()`.

**3. Centralised constants:**
```python
# constants.py — change a threshold here and all services automatically use the new value
MIN_CANDIDATE_AGE = 25
STATION_LOAD_CRITICAL_PERCENT = 100
```
Business rules can be changed by modifying `constants.py` without touching any service code.

### L — Liskov Substitution Principle (LSP)

> *"Objects of a superclass should be replaceable with objects of a subclass without breaking the application."*

While the project does not use deep inheritance hierarchies (which is itself a best practice — "prefer composition over inheritance"), LSP is demonstrated through **polymorphic usage** of `current_user`:

```python
# store.py — current_user can be either an Admin or a Voter object
self.current_user = None   # Holds Admin or Voter interchangeably

# app.py — both types work correctly in the same main loop
if store.current_role == "admin":
    admin_ui.show_dashboard()      # reads current_user as Admin
elif store.current_role == "voter":
    voter_ui.show_dashboard()      # reads current_user as Voter
```

Both `Admin` and `Voter` expose `.full_name`, `.id`, and can be stored in `current_user` without the caller needing to know which type it is. Neither breaks the application when substituted.

All 7 model classes also implement the same serialisation contract (`to_dict()` / `from_dict()`) — `DataStore.save()` and `DataStore.load()` call these methods polymorphically without caring which specific model they're operating on.

### I — Interface Segregation Principle (ISP)

> *"Clients should not be forced to depend on interfaces they do not use."*

Instead of one monolithic "ElectionService" that does everything, the business logic is split into **8 focused services**, each exposing only the methods relevant to its consumers:

```
VoterUI depends on:
  ├── VoteService       (cast_votes, get_available_polls)
  ├── ResultService     (get_position_tally, calculate_turnout)
  ├── AuthService       (hash_password — for password change only)
  └── VoterService      (change_password)

AdminUI (composed of 6 screen handlers, each receiving only its own services):
  ├── CandidateScreens  → CandidateService
  ├── StationScreens    → StationService
  ├── PollScreens       → PollService + CandidateService + StationService
  ├── VoterScreens      → VoterService
  ├── AdminMgmtScreens  → AdminService + AuthService
  └── ResultsScreens    → ResultService + PollService
```

`VoterUI` never sees candidate CRUD methods. `CandidateScreens` never sees voter or result methods. Each consumer depends only on the narrow interface it actually needs.

### D — Dependency Inversion Principle (DIP)

> *"High-level modules should not depend on low-level modules. Both should depend on abstractions."*

This is the most pervasive SOLID principle in the project. **No class creates its own dependencies** — everything is injected via constructors:

```python
# app.py — the composition root wires all dependencies
store = DataStore()                          # Low-level: data layer

auth_service = AuthService(store)            # Mid-level: services receive store
candidate_service = CandidateService(store)
vote_service = VoteService(store)

auth_ui = AuthUI(store, auth_service)        # High-level: UI receives services
admin_ui = AdminUI(store, candidate_service, station_service, ...)
voter_ui = VoterUI(store, vote_service, result_service, auth_service, voter_service)
```

**Before (original monolith):** Functions directly accessed global variables like `candidates`, `voters`, `polls` — tightly coupled to the global namespace.

**After (refactored):** Services receive the `DataStore` through their constructor. UI classes receive services through their constructor. The only place that knows how to wire everything together is `app.py` (the **Composition Root** pattern). This means:
- Services can be tested with a mock `DataStore`
- UI classes can be tested with mock services
- Changing how data is stored only affects `DataStore`, not 8 services and 3 UI classes

---

## Object-Oriented Design Concepts Applied

### 1. Encapsulation

> *"Bundle data with the methods that operate on that data, and restrict direct access to internal state."*

Each model class owns its data and provides meaningful methods to interact with it, rather than exposing raw dictionaries for external code to manipulate:

| Model | Encapsulated Behaviour |
|---|---|
| `Voter` | `has_voted_in_poll(poll_id)` — checks voting history internally |
| `Voter` | `record_vote(poll_id)` — updates the internal `has_voted_in` list |
| `Voter` | `verify()` — sets `is_verified = True` (only the model changes its own state) |
| `Poll` | `open_poll()` / `close_poll()` — manages lifecycle state transitions |
| `Poll` | `has_any_candidates()` — checks nested `PollPosition` objects internally |
| `Poll` | `record_vote()` — increments `total_votes_cast` counter |
| `Candidate` | `is_eligible_for_position(min_age)` — combines active + approved + age checks |
| `Admin` | `is_super_admin()` — hides role string comparison behind a meaningful method |
| `DataStore` | `next_id(entity_type)` — auto-incrementing ID generation with internal counter management |

**Before:** External code directly checked `candidates[cid]["is_active"] and candidates[cid]["is_approved"] and candidates[cid]["age"] >= min_age`.

**After:** External code calls `candidate.is_eligible_for_position(min_age)` — the logic is encapsulated, readable, and changeable in one place.

### 2. Abstraction

> *"Expose only essential features and hide implementation complexity."*

Services provide simple, high-level interfaces that hide complex multi-step operations:

```python
# The UI calls one simple method:
vote_hash = vote_service.cast_votes(voter, poll_id, choices)

# Internally, cast_votes() handles 6 complex steps:
#   1. Look up the poll
#   2. Generate a SHA-256 receipt hash
#   3. Create Vote records for each position choice
#   4. Update the voter's has_voted_in list
#   5. Sync the stored voter object
#   6. Increment the poll's vote counter, log, and save
```

The UI doesn't need to know any of those implementation details. It just calls one method and gets back a receipt hash.

### 3. Composition (over Inheritance)

> *"Prefer composing objects over building deep inheritance trees."*

The project uses **composition** throughout instead of inheritance:

- **`Poll` composes `PollPosition` objects** — a poll *has* positions rather than *being* a position. Each `Poll` contains a list of `PollPosition` instances:
  ```python
  class Poll:
      def __init__(self, ...):
          self.positions = positions or []  # List[PollPosition]
  ```

- **`DataStore` composes all entity collections** — it *has* candidates, voters, polls, etc. rather than inheriting from multiple base classes:
  ```python
  class DataStore:
      def __init__(self):
          self.candidates = {}      # int -> Candidate
          self.voters = {}          # int -> Voter
          self.polls = {}           # int -> Poll
          self.voting_stations = {} # int -> VotingStation
  ```

- **`AdminUI` composes 6 screen handlers** — it *has* a `CandidateScreens`, a `PollScreens`, etc. rather than inheriting from a base class:
  ```python
  class AdminUI:
      def __init__(self, store, candidate_service, station_service, poll_service, ...):
          self._candidate_screens = CandidateScreens(store, candidate_service)
          self._station_screens = StationScreens(store, station_service)
          self._poll_screens = PollScreens(store, poll_service, candidate_service, station_service)
  ```

  Each screen handler in turn composes the services it needs, continuing the composition chain.

No class in the project extends another class. All relationships are composition-based.

### 4. Polymorphism

> *"Objects of different types can be used through the same interface."*

- **Serialisation polymorphism:** All 7 model classes implement `to_dict()` and `from_dict()`. The `DataStore` calls these methods uniformly without knowing the specific model type:
  ```python
  # DataStore.save() — same pattern for every entity type
  "candidates": {str(k): v.to_dict() for k, v in self.candidates.items()},
  "voters":     {str(k): v.to_dict() for k, v in self.voters.items()},
  "polls":      {str(k): v.to_dict() for k, v in self.polls.items()},
  ```

- **Soft-delete polymorphism:** `Candidate`, `Voter`, `Admin`, `VotingStation`, and `Position` all implement `deactivate()`. Services call `entity.deactivate()` without type-specific logic.

- **Session polymorphism:** Both `Admin` and `Voter` objects are stored in `store.current_user` and accessed through a common set of attributes (`.id`, `.full_name`).

---

## Other Clean Code & Design Principles Applied

### DRY — Don't Repeat Yourself

| What Was Duplicated (Original) | How It Was Centralised (Refactored) |
|---|---|
| ANSI color codes and `print()` formatting repeated in 60+ functions | Centralised in `console.py` — all UI modules import `header()`, `error()`, `success()`, `menu_item()`, etc. |
| Password hashing (`hashlib.sha256(...)`) duplicated in 4+ places | Single `AuthService.hash_password()` static method used everywhere |
| Voter card generation logic duplicated | Single `AuthService.generate_voter_card_number()` method |
| Age calculation from DOB repeated in candidate and voter code | Extracted into `CandidateService.validate_candidate_age()` and `AuthService.validate_voter_registration()` |
| `json.dump()`/`json.load()` with error handling repeated | Single `DataStore.save()` / `DataStore.load()` pair |

### KISS — Keep It Simple, Stupid

- Three-layer architecture instead of over-engineering with microservices, event buses, or abstract factories
- Simple dictionary-based collections instead of a full ORM or database
- Plain classes instead of metaclasses, decorators, or framework magic
- One `DataStore` instead of 7 separate repository classes
- JSON file persistence matching the original format exactly

### Separation of Concerns (SoC)

Each layer has one concern and one concern only:

| Layer | Does | Does NOT |
|---|---|---|
| **UI** (`ui/`) | Reads input, formats output, displays menus | Validate business rules, mutate data, compute results |
| **Services** (`services/`) | Validates business rules, orchestrates operations | Print to console, read input, manage raw JSON |
| **Models** (`models/`) | Holds domain state, provides domain methods | Call services, perform I/O, access the DataStore |
| **DataStore** (`store.py`) | Manages collections, handles persistence, tracks session | Validate business rules, format output |
| **Constants** (`constants.py`) | Defines configurable values | Contain any logic |

### High Cohesion

Each module groups tightly related functionality:

- `candidate_service.py` — only candidate operations (create, read, update, delete, search)
- `poll_service.py` — only poll and position operations (they're tightly coupled)
- `result_service.py` — only read-only analytical operations (tallying, statistics, demographics)
- `console.py` — only reusable display primitives (colors, headers, prompts)

### Low Coupling

Modules interact through narrow, well-defined interfaces:

- Services depend only on `DataStore` (one dependency each)
- UI classes depend on services through constructor injection (not global imports)
- Models depend on nothing except `constants.py` (for default values)
- Changing `ResultService` internals has zero impact on `CandidateService`

### Defensive Programming

- **Soft deletes** — entities are deactivated (`is_active = False`) instead of removed, preserving data integrity and vote history
- **Validation before mutation** — services check preconditions before modifying data (e.g., `can_deactivate()` checks for active poll references before allowing deletion)
- **Error return tuples** — services return `(result, None)` or `(None, error_message)` instead of raising exceptions or silently failing
- **Safe deserialization** — `from_dict()` uses `.get(key, default)` so missing fields in old JSON files don't crash the application
- **Poll lifecycle guards** — open polls cannot be edited or deleted; polls without candidates cannot be opened

### Design Patterns Used

| Pattern | Where Applied |
|---|---|
| **Composition Root** | `app.py` — the single place where all dependencies are wired together |
| **Constructor Injection** | Every service and UI class receives dependencies via `__init__` |
| **Strategy Pattern** | `admin_actions` dictionary in `AdminUI` maps choices to handler methods |
| **State Pattern (simplified)** | `Poll` lifecycle: `DRAFT → OPEN → CLOSED` with guard methods (`is_draft()`, `is_open()`, `is_closed()`) |
| **Value Object** | `PollPosition` — exists only within a `Poll`, has no independent identity |
| **Soft Delete** | All major entities use `is_active` flag instead of physical deletion |
| **Audit Trail** | `DataStore.log_action()` records every significant operation with timestamp, actor, and details |

---

## What Was Not Done & Why

| Item | Reason |
|---|---|
| **No new features added** | The exam explicitly states: *"Do not add new features."* The refactoring preserves identical behaviour. |
| **No unit tests** | The exam did not require tests, and adding a test framework would count as a new feature. The application was tested manually and via integration verification to confirm identical behaviour. |
| **No abstract base classes / interfaces** | Python does not require formal interfaces for polymorphism. Adding `abc.ABC` base classes for services would add complexity without practical benefit in a project of this size. The constructor injection pattern already provides the decoupling benefits. |
| **No database (SQLite, etc.)** | The original uses a flat JSON file for persistence. Switching to a database would change the data layer significantly and could be considered a new feature. The JSON format was preserved for identical behaviour. |
| **No type hints** | While type hints improve readability, the original code had none. Adding them across 26 files would be a significant change not required by the exam. The comprehensive docstrings serve a similar documentation purpose. |
| **No configuration file (YAML/TOML)** | Constants are centralised in `constants.py` which is sufficient for this application's scale. An external config file would add deployment complexity not justified by the requirements. |
| **No logging framework** | The original uses a custom audit log (list of dicts). Replacing it with Python's `logging` module would change the audit log format and break identical behaviour. |
| **No role-based access enforcement in services** | The original code does not enforce role checks in business logic — it relies on the UI showing different menus to different roles. Moving role checks into services would change the architecture and potentially alter behaviour edge cases. The original pattern was preserved. |

---

## How to Run

```bash
python3 app.py
```

**Default admin credentials:** `admin` / `admin123`

**Quick test path:**
1. Log in as admin
2. Create a voting station
3. Register a voter (from the login menu)
4. Log in as admin → verify the voter
5. Create a position → create a poll → assign candidates → open the poll
6. Log in as the voter → cast a vote
7. Log in as admin → close the poll → view results

---

## Original Features Preserved

All features from the original monolith work identically:

- Role-based access (super_admin, election_officer, station_manager, auditor, voter)
- Candidate CRUD with eligibility checks (age 25–75, education level, criminal record)
- Voting station management with capacity tracking
- Position and poll lifecycle (draft → open → closed → reopened)
- Voter self-registration with auto-generated 12-character card numbers
- Admin voter verification (individual and bulk)
- Ballot casting with duplicate prevention and abstention support
- SHA-256 vote receipt hash generation
- Result tallying with ASCII bar charts and turnout percentages
- Voter demographics breakdown (gender, age groups)
- Station load analysis (capacity utilisation warnings)
- Party and education distribution reports
- Station-by-station result breakdowns
- Filtered audit log (by action type, by user, last N entries)
- JSON data persistence (`evoting_data.json`)
- Masked password input with yellow asterisks
- ANSI-colored themed console interface

---

## Team Contributions

| Member | Modules | Focus Area |
|---|---|---|
| **Joseph** | `constants.py`, `models/` (all 7 model files), `store.py` | Data layer — domain models, named constants, persistence |
| **Anna** | `ui/console.py`, `ui/auth_ui.py`, `services/auth_service.py`, `services/station_service.py`, `services/candidate_service.py`,| UI framework — colors, formatting, authentication flow |
| **Precious** |   `ui/admin/candidate_screens.py`, `ui/admin/station_screens.py`, `ui/admin/poll_screens.py`, `ui/admin/voter_screens.py`, | Candidate & station management |
| **Oscar** | `services/poll_service.py`, `services/vote_service.py`, `services/voter_service.py`, `services/admin_service.py`, `ui/admin/admin_mgmt_screens.py` | Poll lifecycle, voting process, voter/admin management |
| **Absolom** | `services/result_service.py`, `ui/voter_ui.py`, `ui/admin/results_screens.py`, `ui/admin/admin_ui.py`, `ui/admin/__init__.py`, `app.py`, `README.md` | Results & reports, voter UI, admin coordinator, integration, documentation |
