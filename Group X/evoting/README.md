# E-voting-App

We were given a working National E-Voting console application packed into one single file. It had about 1800 lines of code and handled everything: candidates, voters, polling stations, voting, results, different user roles, you name it. The code worked perfectly but it was a monolith - everything mixed together, global variables everywhere, and no clear structure. If you wanted to change one thing, you had to understand the whole file.

# OUR TASK.
We had to breakdown this monolith into a proper modular Python project while keeping the exact same functionality. Same menus, same prompts, same outputs. No new features, just cleaner code. And in oder to Archive this the team had to impliment Modular Design, Object-Oriented Design, Separation of Concerns, and Clean Code Principles.

# HOW WE HANDLED THE TASK.
We split the work based on natural boundaries in the system:

* Owen took the foundation lead.
* Aturinda took lead on the Models.
* Anthony took point on the Core Services.
* Danny handled the Poll and Voter Services.
* Kirabo Handled the UI & Display.


# How We Organized the Code
Here's what our project folder looks like:
evoting/
├── main.py                      # Entry point: initializes and runs the application
├── storage/
│   └── data_store.py            # Centralized data persistence layer
├── utils/
│   └── helpers.py               # Shared utility and helper functions
├── models/
│   ├── admin.py                 # Admin user data structure
│   ├── candidate.py             # Candidate profile data structure
│   ├── voter.py                 # Registered voter data structure
│   ├── poll.py                  # Election/Poll configuration
│   ├── position.py              # Election positions (e.g., President, Senator)
│   ├── station.py               # Voting location/polling station details
│   └── vote.py                  # Individual ballot and vote data structure
├── services/
│   ├── auth_service.py          # Authentication and registration logic
│   ├── candidate_service.py     # Business logic for candidate management
│   ├── station_service.py       # Business logic for station management
│   ├── poll_service.py          # Management of poll lifecycles and timing
│   ├── vote_service.py          # Core logic for casting votes and calculating results
│   ├── voter_service.py         # Business logic for voter management
│   └── admin_service.py         # Business logic for administrative tasks
├── ui/
│   ├── display.py               # UI components: formatting, colors, and layouts
│   ├── admin_ui.py              # Screen definitions for administrative users
│   └── voter_ui.py              # Screen definitions for voters
└── data/
    └── evoting_data.json        # JSON database for persistent storage  
      
   



 

