# E-voting-App

We were given a working National E-Voting console application packed into one single file. It had about 1800 lines of code and handled everything: candidates, voters, polling stations, voting, results, different user roles, you name it. The code worked perfectly but it was a monolith - everything mixed together, global variables everywhere, and no clear structure. If you wanted to change one thing, you had to understand the whole file.

# OUR TASK.
We had to breakdown this monolith into a proper modular Python project while keeping the exact same functionality. Same menus, same prompts, same outputs. No new features, just cleaner code. And in oder to Archive this the team had to impliment Modular Design, Object-Oriented Design, Separation of Concerns, and Clean Code Principles.

# HOW WE HANDLED THE TASK.
We split the work based on natural boundaries in the system:

Owen took the foundation - the data storage and main entry point. Which basically means that he built the backbone that everyone else depends on.

Aturinda handled all the data models. She created classes for Candidates, Voters, Admins, Polls, Positions, Voting Stations, and Votes.

Anthony focused on core services - authentication, candidate management, and station management. These are the basic CRUD operations.

Danny handled the- poll lifecycle, voting logic, results calculation, and admin management. 

Kirabo did the UI  - the display helpers, admin dashboard, voter dashboard, and this README.

