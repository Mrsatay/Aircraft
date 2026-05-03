# Thesis Defense Slide Details

This file contains slide-ready content for the thesis defense presentation of the `Aircraft_Test_Fault_Django` project.

## Page 1: Project Information

Slide title:

Aircraft Test Fault Closed-Loop Management System

Suggested content:

- Project Title: Aircraft Test Fault Closed-Loop Management System
- Student Name: English name / Chinese name
- Supervisor Name: Supervisor name
- Major / Class: Computer Science / related program

Short speaking note:

"Good morning/afternoon. My project is titled Aircraft Test Fault Closed-Loop Management System. The purpose of this system is to manage aircraft test faults from initial reporting until final verification and closure."

## Page 2: Main Development Technologies and Tools

Slide title:

Main Development Technologies and Tools

Slide content:

- Backend Framework: Django
- Programming Language: Python
- Database: PostgreSQL
- Frontend: HTML, CSS, JavaScript
- UI Framework: Bootstrap
- Icons and UI Assets: Bootstrap Icons, Font Awesome
- Data Visualization: Chart.js
- Authentication: Django Authentication System
- AI Integration: OpenRouter API
- Development Tools: Visual Studio Code, Git, PostgreSQL / pgAdmin

Short speaking note:

"This system was developed using Django as the backend framework and Python as the main programming language. PostgreSQL is used as the database. The frontend is built with HTML, CSS, JavaScript, and Bootstrap. Chart.js is used for dashboard visualization, and OpenRouter API is integrated to support AI-based fault description and fault explanation."

## Page 3: Main Functions

Slide title:

Main Functions and System Module Diagram

Important note:

This slide should introduce the main system functions using a system module diagram. The focus is not only the website menu structure, but how the main modules work together to support aircraft test fault closed-loop management.

Recommended module diagram:

```text
                        Aircraft Test Fault Closed-Loop
                            Management System
                                      |
        ---------------------------------------------------------------
        |              |              |              |                 |
 User Authentication  Aircraft     Fault Recording  Closed-Loop    Dashboard
   and RBAC           Management   and Tracking     Workflow       and Reporting
        |              |              |              |                 |
 Login / Logout       Aircraft      Fault CRUD      New             Charts
 Registration         Data          Detail View     Under Analysis  Metrics
 Role Permission      Reference     Filtering       Root Cause      Reports
 Access Control                     Sorting         Repair
                                    Pagination      Verified Closed
                                      |
                         Status History and Traceability
                                      |
                         AI-Assisted Fault Support
```

Slide content:

- User Authentication and RBAC Management
- Aircraft and Resource Management
- Fault Recording and Tracking
- Closed-Loop Workflow Management
- Status History and Traceability
- Dashboard and Reporting
- AI-Assisted Fault Support

Function descriptions:

- User Authentication and RBAC Management: Manages login, logout, registration, user roles, and role-based access permissions.
- Aircraft and Resource Management: Stores aircraft information used as the reference for fault records.
- Fault Recording and Tracking: Supports fault creation, list view, detail view, editing, deletion, filtering, sorting, and pagination.
- Closed-Loop Workflow Management: Controls fault progress from `New` to `Verified Closed`.
- Status History and Traceability: Records each workflow status change for monitoring and audit purposes.
- Dashboard and Reporting: Provides charts, key metrics, recent activity, and filtered report summaries.
- AI-Assisted Fault Support: Generates fault descriptions and explanations using LLM integration with local fallback support.

Short speaking note:

"This slide introduces the main functions of the system through a system module diagram. The first module is User Authentication and RBAC Management, which controls login and access permissions based on user roles. Aircraft Management stores aircraft reference data used when creating fault records. The core function is Fault Recording and Tracking, where users can create, view, edit, filter, sort, and monitor aircraft test faults. After a fault is recorded, it is processed through the Closed-Loop Workflow from New until Verified Closed. Each workflow change is stored in Status History to support traceability and audit. The system also provides Dashboard and Reporting for fault statistics, and AI-Assisted Fault Support to help generate fault descriptions and explanations."

Simpler speaking version:

"The main functions of this system include RBAC-based user access control, aircraft data management, fault recording and tracking, closed-loop workflow management, status history traceability, dashboard reporting, and AI-assisted fault support. The most important part is that the system does not only record faults, but also tracks the whole fault handling process until the fault is verified and closed."

## Page 4: Development Status

Slide title:

Development Status

Suggested layout:

Use two columns:

- Completed Functions
- Uncompleted Functions / Future Improvements

### Completed Functions

- User login, logout, registration, and role management
- Administrator user management
- Aircraft registry and aircraft data management
- Fault creation, detail view, edit, and delete
- Fault list with filtering, sorting, and pagination
- Closed-loop workflow status management
- Mandatory `Analysis Findings` when moving to `Under Analysis`
- Mandatory `Root Cause` when moving to `Root Cause Identified`
- `Verified Closed` restricted to Admin and Test Manager
- Assignment restricted to Test Engineer and Maintenance Engineer
- Status history tracking for workflow traceability
- Dashboard visualization using Chart.js
- Basic reporting with filters and summary statistics
- AI-based fault description generation
- AI-based fault explanation generation
- PostgreSQL database integration
- 60-minute automatic session timeout

### Uncompleted Functions / Future Improvements

- Fully role-tailored dashboard for each user role
- Component and subsystem lookup table management
- PDF or Excel report export
- Email or notification system for assigned faults
- Production server deployment
- More comprehensive automated testing
- Advanced analytics such as fault trend prediction
- Advanced AI recommendation for maintenance actions

Short speaking note:

"At the current stage, the core functions of the system have been completed, including authentication, role control, aircraft management, fault lifecycle management, workflow validation, dashboard visualization, reporting, AI support, and PostgreSQL integration. The remaining items are future improvements, such as role-specific dashboard customization, lookup table management, report export, notification, deployment, and more advanced analytics."

## Very Short Defense Version

If the presentation time is limited, use this version.

Page 2:

- Django, Python, PostgreSQL
- HTML, CSS, JavaScript, Bootstrap
- Chart.js for visualization
- Django Authentication for login and role control
- OpenRouter API for AI support

Page 3:

- User and role management
- Aircraft management
- Fault recording and tracking
- Closed-loop workflow management
- Dashboard and reporting
- AI-assisted fault support

Page 4:

Completed:

- Authentication and role control
- Aircraft management
- Fault CRUD
- Filtering, sorting, and pagination
- Workflow validation and status history
- Dashboard and reports
- AI support
- PostgreSQL integration

Future Improvements:

- Role-specific dashboard
- Subsystem lookup table
- PDF/Excel export
- Notification system
- Production deployment
- Advanced analytics and AI recommendation
