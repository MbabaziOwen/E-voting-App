# National E-Voting System

A modular console application for managing national elections. Supports candidate registration, voter management, poll creation, ballot casting, and real-time result tallying.

---

## Project Structure

```
evoting/
├── main.py                  # Application entry point
├── data/
│   └── evoting_data.json    # Persistent storage
├── models/                  # Data classes
│   ├── admin.py
│   ├── candidate.py
│   ├── poll.py
│   ├── position.py
│   ├── station.py
│   ├── vote.py
│   └── voter.py
├── services/                # Business logic
│   ├── auth_service.py      # Login/registration
│   ├── admin_service.py     # Admin management
│   ├── candidate_service.py # Candidate operations
│   ├── poll_service.py      # Poll & position management
│   ├── station_service.py   # Voting station operations
│   ├── voter_service.py     # Voter verification
│   └── vote_service.py      # Ballot casting & results
├── ui/                      # User interface
│   ├── display.py           # Print helpers and colors
│   ├── admin_ui.py          # Admin menus
│   └── voter_ui.py          # Voter menus
├── storage/
│   └── data_store.py        # Central data container
└── utils/
    └── helpers.py           # Hash, card generator, audit log
```

## Problems with the Original Code

The original application was a single large file with several issues:

- Global variables used everywhere  
- Print statements mixed with business logic  
- No classes or object-oriented structure  
- Tightly coupled code  
- Difficult to maintain  
- No single source of truth for data  

## How We Fixed It

**1. Modular Design**  
We split the code into logical folders:

- `models/` → pure data structures  
- `services/` → business operations  
- `ui/` → user interface  
- `storage/` → data persistence  
- `utils/` → helper functions  

**2. Object-Oriented Design**  
Every entity became a class (Candidate, Voter, Poll, etc.). Services are classes that receive a `DataStore` instance. UI is encapsulated in `AdminUI` and `VoterUI` classes. The `DataStore` class centralizes all application state.

**3. Separation of Concerns**

- UI layer only prints menus and calls service methods.
- Service layer implements business rules and never prints directly.
- Storage layer manages data persistence.
- Model layer contains pure data structures with no logic.

**4. Clean Code**

- Meaningful function names  
- No code duplication  
- Single responsibility per function  
- Consistent naming conventions  

## Key Design Decisions

**DataStore – Single Source of Truth**

One object holds all application state. Every service receives the same store instance, eliminating global variables.

**Services Receive the Store**

All data access goes through `self.store`.

**UI Calls Services**

The UI layer never implements business logic. It only calls service methods and displays results.

## How to Run

### 1. Create the data folder

```bash
mkdir -p data
echo "{}" > data/evoting_data.json
```

### 2. Run the application

```bash
python main.py
```

### 3. Default admin credentials

- **Username:** `admin`  
- **Password:** `admin123`

## Features Preserved

- Candidate management with age, education, and criminal record validation  
- Voting station management  
- Position and poll lifecycle (draft, open, closed)  
- Voter registration with verification  
- Four admin roles (`super_admin`, `election_officer`, `station_manager`, `auditor`)  
- Ballot casting with duplicate prevention  
- Result tallying with bar charts  
- Turnout statistics  
- Station-wise results  
- Full audit log  
- Same menus, prompts, and outputs as the original system  

## Team Contributions

| Person | Role | Files |
|------|------|-------|
| Owen | Foundation Lead | helpers.py, data_store.py, main.py |
| Aturinda | Models Lead | All model files (admin.py, candidate.py, poll.py, position.py, station.py, vote.py, voter.py) |
| Anthony | Core Services | auth_service.py, candidate_service.py, station_service.py |
| Danny | Poll & Vote Services | poll_service.py, vote_service.py, voter_service.py, admin_service.py |
| Kirabo | UI Lead | display.py, admin_ui.py, voter_ui.py, README.md |

## Testing Checklist

- [ ] Every folder has `__init__.py`  
- [ ] `data/evoting_data.json` exists  
- [ ] No global variables remain  
- [ ] No model file contains `print()` or `input()`  
- [ ] End-to-end workflow works:  
  `create station → create poll → register voter → verify → vote → view results`

---

*Built for UCU Software Construction 2026*
