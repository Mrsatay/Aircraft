# Design Task and Design Requirement

## 1. Design Task

The design task of this project is to develop a web-based Aircraft Test Fault Closed-Loop Management System. The system is used to record, monitor, analyze, and close aircraft test faults through a structured digital workflow. It replaces manual fault tracking methods such as paper records or spreadsheets, so every fault can be traced from initial reporting until final verification.

The main task is to implement a closed-loop fault lifecycle. Each fault must move through controlled stages: `New`, `Assigned`, `Under Analysis`, `Root Cause Identified`, `Fix In Progress`, `Resolved`, and `Verified Closed`. This workflow ensures that every problem is assigned, analyzed, repaired, verified, and documented properly.

The project is implemented as a Django web application. The system is divided into several modules: user management, aircraft management, fault management, dashboard, reporting, and AI-assisted fault support. The frontend uses HTML, CSS, JavaScript, Bootstrap, Bootstrap Icons, Font Awesome, and Chart.js. The backend uses Python and Django, with PostgreSQL as the main database configuration.

The system also applies role-based access control. Admin manages users and system data. Test Engineer reports faults and updates assigned faults. Maintenance Engineer analyzes faults and records technical findings. Test Manager monitors all faults, assigns engineers, generates reports, and verifies final closure.

## 2. Design Requirement

The system must provide authentication and role-based access for Admin, Test Engineer, Maintenance Engineer, and Test Manager, with functions for aircraft management, fault management, dashboard, reporting, and optional AI-assisted fault explanation. Fault records must follow the closed-loop workflow `New -> Assigned -> Under Analysis -> Root Cause Identified -> Fix In Progress -> Resolved -> Verified Closed`, with required analysis findings, root cause information, and status history for traceability. The main data entities are `UserProfile`, `Aircraft`, `Fault`, and `StatusHistory`, where each fault is connected to an aircraft, responsible users, and its workflow history. The system is implemented using Django, Python, PostgreSQL, Django ORM, Bootstrap, and Chart.js, with login protection and role-based permission control for sensitive operations.
