# E-Voting Console Application (Refactored)

## Overview

This project is a refactored version of the National E-Voting console
application. The goal of the refactor was to improve the structure,
validation, and data handling of the system while keeping the original
behaviour exactly the same.

All menus, prompts, and outputs remain identical to the original
application. The improvements mainly focus on the internal design and
architecture of the system so that the code is easier to maintain,
extend, and understand.

---

## How to Run the Program

From the refactored directory:

```bash
python e_voting_console_app.py
```

Or from the project root:

```bash
python refactored/e_voting_console_app.py
```

**Default Admin Login**

- Username: `admin`
- Password: `admin123`

The application stores its data in: `evoting_data.json`

---

## Project Structure

```
refactored/
├── app/
│   ├── admin_dashboard.py
│   ├── voter_dashboard.py
├── ui/
│   ├── console.py
│   ├── themes.py
├── services/
│   ├── auth_service.py
│   ├── candidate_service.py
│   ├── voter_service.py
│   ├── poll_service.py
│   ├── voting_service.py
│   ├── validation.py
│   ├── audit_service.py
├── data/
│   ├── store.py
│   ├── repository.py
│   ├── context.py
├── models/
│   ├── constants.py
└── e_voting_console_app.py
```

# Design Approach

During the refactoring process, the main focus was to apply software
construction principles such as modularity, separation of concerns, and
clean code practices.

## Modular Design

The system is divided into several modules so that each file performs a
specific function.

For example:

- UI modules handle display and user input
- Service modules handle business logic
- Data modules handle storage and retrieval

---

## Object-Oriented Programming and Design Principles Applied

Several Object-Oriented Programming (OOP) and Object-Oriented Design
(OOD) principles were applied to improve the organization of the system.

## Encapsulation

Encapsulation was used to group related data and functionality together.

Repository classes manage how entities are stored and retrieved from the
data store.

Examples: CandidateRepository, VoterRepository, PollRepository, StationRepository

---

## Abstraction

Abstraction was applied by hiding implementation details behind service
functions.

Examples:

- `candidate_service.create()`
- `voter_service.register()`
- `poll_service.create()`

The UI layer simply calls these functions without needing to know how
the internal logic works.

---

## Single Responsibility Principle

Each module is responsible for a single task.

Examples:

- `ui/console.py` — handles console input and output
- `services/validation.py` — handles validation
- `services/auth_service.py` — handles authentication
- `services/voting_service.py` — handles voting logic
- `data/store.py` — handles data persistence

---

## Separation of Concerns

The application is divided into layers:

- **UI Layer** — user interaction
- **Service Layer** — application logic
- **Data Layer** — storage and retrieval

This ensures changes in one layer do not affect the others.

---

## Data Handling

All system data is stored in: `evoting_data.json`

The system loads this data when the application starts and saves it when
changes occur.

Unique identifiers are managed using counters such as:

-   candidate_id_counter
-   voter_id_counter
-   poll_id_counter

---

## Error Handling and Validation

Strong validation and error handling were added during refactoring.

If a user enters invalid input, the system:

1.  Displays an error message
2.  Requests the input again
3.  Continues running normally

---

## Date Validation

Dates must follow the format: `YYYY-MM-DD`

Additional checks ensure:

-   dates exist
-   date of birth is not in the future
-   poll end date occurs after poll start date

---

## Phone Number Validation

Phone numbers must:

-   start with 07
-   contain exactly 10 digits

Example: `0712345678`

---

## Email Validation

Emails must follow a valid format such as: `name@example.com`

Regular expressions are used to validate the email structure.

---

## Required Fields

Fields such as names, titles, and descriptions cannot be empty.

If a required field is empty, the system asks the user to enter the
value again.

---

## Logical Validation

The system also checks logical rules such as:

-   poll end date must be after start date
-   national IDs must be unique
-   voters cannot vote more than once
-   candidates must meet age and education requirements

---

## Security Measures

## Password Hashing

Passwords are stored using SHA-256 hashing instead of plain text.

Example: `hashlib.sha256(password.encode()).hexdigest()`

---

## Audit Logging

The system records important actions in an audit log, including:

-   logins
-   candidate creation
-   poll creation
-   vote casting
-   admin actions

---

## Constraints Implemented

- **Candidate Age** — must fall within allowed range
- **Phone Number** — must start with 07
- **Email** — must follow valid format
- **Poll Dates** — end date must be after start date
- **Seats per Position** — limited range
- **Required Fields** — cannot be empty

