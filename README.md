# E-voting System Refactoring Report

## Project Overview
This project is a refactor of a monolithic E-voting console application. The original application was contained within a single file, violating principles of modularity, separation of concerns, and clean code. This refactored version adheres to the **Software Construction** course requirements for high-quality, object-oriented design.

## Group Members

- Geno Owor Joshua
- Nicole Johnson
- Alinda Rebecca
- Zahara Zinda
- Kisa Emmanuel

## Design Decisions & Principles

### 1. Modular Design
The application is split into four primary packages under the `src/` directory:
- `models/`: Contains pure data entities (Classes for User, Voter, Candidate, etc.).
- `data/`: Handles data persistence and JSON serialization.
- `services/`: Contains the business logic and rules governing the domain.
- `ui/`: Handles the console presentation layer and menu routing.

### 2. Object-Oriented Design (OOD)
The refactored project uses formal classes and inheritance (e.g., `Admin` and `Voter` inheriting from `User`). 
- **Encapsulation**: Domain models use dataclasses for clean state management, while logic is encapsulated within service classes.
- **Abstraction**: High-level services abstract away the complexities of the data store and domain rules from the UI.

### 3. Separation of Concerns
- **UI Logic**: All input/output (ANSI colors, menu layout) is strictly in `src/ui/`.
- **Business Logic**: Rules like age requirements for candidates or duplicate vote prevention are strictly in `src/services/`.
- **Data Persistence**: The `DataStore` handles the reading/writing of `evoting_data.json` independently, returning typed objects instead of raw dictionaries.

### 4. Clean Code Quality
- **Meaningful Naming**: Functions and variables follow clear, descriptive conventions.
- **DRY (Don't Repeat Yourself)**: Common UI elements like headers and tables are consolidated into a theme utility module.

## Project Structure
```bash
E-voting-App/
├── evoting_data.json       # Persisted database
├── src/
│   ├── main.py             # Entry point
│   ├── models/             # Domain Entities (OOP)
│   ├── data/               # Persistence Layer (Json Store)
│   ├── services/           # Business Logic Layer
│   └── ui/                 # Presentation Layer
└── README.md               # This Report
```

## How to Run
Ensure you have Python 3 installed. Navigate to the root folder and run:
```bash
python3 src/main.py
```

## Verification
The refactored version has been tested to match the original application's behavior 100%, including:
- Interactive menus and exact wording.
- Data integrity (importing/exporting JSON).
- Security (password masking and hashing).
- Roles (Super Admin, Officer, Voter, etc.).
