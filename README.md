# E-voting-App
**Secure, auditable, terminal-based electronic voting simulation**

Current status: **prototype / proof-of-concept** written as one large script  
Target goal: modular, testable, maintainable codebase following clean code & SOLID principles

## Project Goals (Refactoring Focus)

- Apply **Single Responsibility Principle** — split giant functions and god-objects
- Eliminate **deep nesting** and arrow anti-pattern
- Remove **mixed responsibilities** (calculation + printing + state mutation)
- Replace global variables with proper dependency injection / context objects
- Use **encapsulation** and protect invariants (especially around voting & audit)
- Move toward **composition over inheritance** where domain classes appear
- Improve **naming**, eliminate **magic values**, add **type hints**
- Separate **presentation** (CLI rendering) from **business logic** and **data access**
- Introduce proper **exception handling strategy** instead of print-and-return
- Make **audit logging**, **vote integrity** and **data persistence** more robust