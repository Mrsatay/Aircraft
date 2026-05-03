# Thesis System Design Notes for `Aircraft_Test_Fault_Django`

This document is prepared from the actual implementation of the Django project in this folder.  
Its purpose is to provide thesis-ready material for the formal project description, ERD explanation, workflow description, and system architecture description.

## 1. Formal Technical Narrative

The developed system is a web-based Aircraft Test Fault Closed-Loop Management System implemented using the Django framework and PostgreSQL database. The system is designed to support the full lifecycle of aircraft test fault handling, starting from initial fault reporting, assignment, technical analysis, corrective action, and final verification closure. The main objective of the platform is to provide a structured and traceable management environment for aircraft test faults so that operational issues can be documented, monitored, and resolved in a controlled manner.

From the implementation perspective, the system is divided into several functional modules, namely user management, aircraft management, fault management, dashboard visualization, reporting, and AI-assisted fault support. The `accounts` module manages authentication and role-based access control. The `aircraft` module stores master aircraft data that becomes the reference for fault records. The `faults` module acts as the core of the system by storing fault reports, assignment data, severity level, subsystem category, engineering findings, root cause information, corrective actions, and closure information. The `dashboard` and `reports` modules provide summarized and filtered views of operational data. In addition, the `ai_tools` module integrates OpenRouter-based LLM support to help generate fault descriptions and explanations.

The system applies a closed-loop workflow mechanism to ensure that each fault progresses through predefined engineering stages. A fault begins in the `New` state and can continue through `Assigned`, `Under Analysis`, `Root Cause Identified`, `Fix In Progress`, `Resolved`, and `Verified Closed`. Each valid state transition is controlled in the service layer and recorded in a dedicated status history table. This mechanism improves traceability, accountability, and consistency in the handling of test-related aircraft faults.

In database design, the application uses Django's built-in `User` model as the base identity entity and extends it through the `UserProfile` model to store the operational role of each user. Fault data is linked to aircraft records and to multiple user roles, such as reporter, assignee, and closer. Status transitions are stored separately in a `StatusHistory` entity to preserve workflow history. This structure supports both daily operational usage and future analytical expansion.

Overall, the implemented Django system represents a practical digital platform for managing aircraft test faults in a structured and traceable way. Compared with fragmented or manual recording methods, the system provides stronger process visibility, better role coordination, and improved monitoring of the fault lifecycle.

## 2. ERD Description

### 2.1 Main Entities

The main entities implemented in the system are:

- `User`
- `UserProfile`
- `Aircraft`
- `Fault`
- `StatusHistory`

### 2.2 Entity Relationship Explanation

1. `User` and `UserProfile`

The system uses Django's default `User` model to store authentication data such as username, password, and basic account information.  
To support role-based access control, each user is associated with exactly one `UserProfile` record through a one-to-one relationship.

Relationship:
- One `User` has one `UserProfile`
- One `UserProfile` belongs to one `User`

Purpose:
- store role information such as `Admin`, `Test Engineer`, `Maintenance Engineer`, and `Test Manager`

2. `Aircraft` and `Fault`

Each fault must be linked to one aircraft because fault records are always associated with a specific aircraft under testing or maintenance observation.  
An aircraft can have many fault records over time.

Relationship:
- One `Aircraft` can have many `Fault` records
- One `Fault` belongs to one `Aircraft`

3. `User` and `Fault`

The `Fault` entity is linked to the `User` model through several foreign keys to represent different responsibilities in the fault handling process.

Relationship:
- One `User` can report many faults through `reported_by`
- One `User` can be assigned to many faults through `assigned_to`
- One `User` can close many faults through `closed_by`

Purpose:
- separate operational roles in the fault lifecycle
- preserve accountability of each engineering action

4. `Fault` and `StatusHistory`

The system stores workflow transitions in a separate `StatusHistory` entity.  
Each status update of a fault generates a history record containing the previous status, new status, actor, notes, and timestamp.

Relationship:
- One `Fault` can have many `StatusHistory` records
- One `StatusHistory` belongs to one `Fault`

5. `User` and `StatusHistory`

The user who performs the workflow update is stored in `changed_by`.

Relationship:
- One `User` can create many `StatusHistory` records
- One `StatusHistory` may reference one `User`

### 2.3 ERD Narrative for Thesis

The ERD of the system is centered on the `Fault` entity as the core transaction table. The `Fault` table is connected to the `Aircraft` table to identify the aircraft affected by a fault. It is also connected to the `User` table through multiple foreign keys representing the reporting user, assigned engineer, and closing user. To support role-based access control, the `User` entity is extended by the `UserProfile` entity in a one-to-one relationship. Furthermore, each fault is linked to multiple `StatusHistory` records to preserve the closed-loop workflow trace. This ERD structure reflects both operational data management and engineering traceability requirements.

### 2.4 Compact ERD Mapping

- `User` 1..1 `UserProfile`
- `Aircraft` 1..* `Fault`
- `User` 1..* `Fault` as `reported_by`
- `User` 1..* `Fault` as `assigned_to`
- `User` 1..* `Fault` as `closed_by`
- `Fault` 1..* `StatusHistory`
- `User` 1..* `StatusHistory` as `changed_by`

## 3. Workflow Diagram Description

### 3.1 Workflow States

The fault workflow implemented in the system is:

`New -> Assigned -> Under Analysis -> Root Cause Identified -> Fix In Progress -> Resolved -> Verified Closed`

### 3.2 Transition Rules

The workflow logic is defined in the service layer through controlled transitions:

- `New` can move to `Assigned`
- `Assigned` can move to `Under Analysis`
- `Under Analysis` can move back to `Assigned` or forward to `Root Cause Identified`
- `Root Cause Identified` can move back to `Under Analysis` or forward to `Fix In Progress`
- `Fix In Progress` can move back to `Root Cause Identified` or forward to `Resolved`
- `Resolved` can move back to `Fix In Progress` or forward to `Verified Closed`
- `Verified Closed` is the final state

The implementation also allows the current state to remain unchanged in some transitions, which supports partial updates without forcing a workflow jump.

### 3.3 Workflow Explanation for Thesis

The workflow diagram of the system represents a closed-loop engineering process for aircraft test fault handling. Initially, a newly reported fault enters the `New` status. After triage, the fault is moved to `Assigned`, where responsibility is given to an engineer or relevant operational personnel. The fault then moves to `Under Analysis`, indicating that technical investigation has begun. Once the root cause is identified, the workflow proceeds to `Root Cause Identified`, followed by `Fix In Progress` when corrective action is being executed. After the corrective action is completed, the fault enters the `Resolved` state. The final state, `Verified Closed`, indicates that the fix has been verified and the fault has been formally closed.

This workflow ensures that each aircraft fault is not merely recorded but is processed through a complete engineering lifecycle with traceable stages. Every valid change is recorded in the `StatusHistory` entity to support auditing and maintenance analysis.

### 3.4 Short Version for Figure Caption

Figure X illustrates the closed-loop fault workflow implemented in the system. A fault progresses from `New` to `Assigned`, `Under Analysis`, `Root Cause Identified`, `Fix In Progress`, `Resolved`, and finally `Verified Closed`. Each transition is validated in the service layer and recorded in the status history table.

## 4. System Architecture Diagram Description

### 4.1 Architecture Overview

The system follows a typical Django-based web application architecture consisting of presentation, application, service, data access, and database layers. User requests are sent from the browser interface to Django URL routing, which dispatches them to the corresponding view functions. Business rules, especially for workflow validation and fallback logic, are handled in the service layer. Data persistence is managed through Django ORM models, which interact with the PostgreSQL database.

### 4.2 Main Architectural Components

1. Presentation Layer

The presentation layer is composed of HTML templates, Bootstrap-based UI components, CSS styling, and JavaScript interactions.  
This layer includes pages such as dashboard, fault list, create fault form, fault detail page, reports page, aircraft management page, and user management page.

2. URL Routing Layer

The root URL configuration distributes requests to application modules:

- `/accounts/`
- `/dashboard/`
- `/faults/`
- `/aircraft/`
- `/reports/`
- `/ai/`

This routing structure supports modular development and separates system functionality into independent Django apps.

3. View Layer

The view layer handles HTTP requests and responses.  
Examples include:

- login and registration views in `accounts/views.py`
- dashboard rendering in `dashboard/views.py`
- fault CRUD and workflow update in `faults/views.py`
- reporting logic in `reports/views.py`
- AI endpoints in `ai_tools/views.py`

4. Service Layer

The service layer contains reusable business logic, especially in `faults/services.py`.  
This layer validates workflow transitions, synchronizes closure state, creates status history records, and generates local fallback text for AI support.

5. Model Layer

The model layer defines persistent entities such as `UserProfile`, `Aircraft`, `Fault`, and `StatusHistory`.  
These models are implemented using Django ORM and provide structured interaction with PostgreSQL.

6. External AI Integration

The system also integrates an external LLM service through OpenRouter.  
The AI module is used for:

- generating fault descriptions
- generating fault explanations

If the external LLM is unavailable, the system provides a local fallback template so that the feature remains operational.

### 4.3 Architecture Explanation for Thesis

From an architectural perspective, the Aircraft Test Fault Closed-Loop Management System adopts a modular web architecture based on Django. The frontend layer is responsible for user interaction and data entry, while the backend layer processes requests, applies workflow rules, and manages database transactions. The separation of modules into `accounts`, `aircraft`, `faults`, `dashboard`, `reports`, and `ai_tools` improves maintainability and clarity. The workflow logic is intentionally centralized in the service layer so that the transition rules remain consistent regardless of which interface triggers the update. PostgreSQL is used as the primary data storage layer, and OpenRouter is used as an optional intelligent service layer for LLM-assisted text generation.

### 4.4 Short Version for Figure Caption

Figure Y shows the system architecture of the Django-based aircraft fault management platform. User requests from the web browser are routed through Django URL configuration to the corresponding views. Business rules are processed in the service layer, data is stored through ORM models in PostgreSQL, and optional AI functions are handled through OpenRouter integration.

## 5. Suggested Diagram Labels

### 5.1 ERD Figure Title

Entity Relationship Diagram of the Aircraft Test Fault Closed-Loop Management System

### 5.2 Workflow Figure Title

Closed-Loop Fault Handling Workflow of the Aircraft Test Fault Management System

### 5.3 Architecture Figure Title

System Architecture of the Django-Based Aircraft Test Fault Closed-Loop Management System

## 6. CRUD Design and Module Algorithms

### 6.1 CRUD Overview

The system implements CRUD operations across its main modules to support the complete management lifecycle of aircraft fault data. In practical usage, the most important CRUD processes are concentrated in the `faults`, `aircraft`, and `accounts` modules.

The `faults` module provides full create, read, update, and delete operations for fault records. The `aircraft` module provides create, read, and update operations for aircraft master data. The `accounts` module provides create, read, update, and delete operations for user management, while authentication itself is handled separately through login and logout functions. In addition, the system includes operational read and update logic in the `dashboard`, `reports`, and `ai_tools` modules, although these modules are not conventional CRUD modules in the strict database sense.

From the perspective of software engineering, CRUD operations in this system are not only direct database actions but are integrated with validation rules, role-based access control, workflow checking, and status history recording. Therefore, the CRUD process is implemented as a combination of URL routing, view processing, form validation, business logic services, and ORM-based persistence.

### 6.2 Fault Module CRUD Algorithm

The `faults` module is the central module of the system. Its CRUD operations are implemented through the following main views:

- `fault_list_view`
- `create_fault_view`
- `fault_detail_view`
- `fault_edit_view`
- `fault_delete_view`
- `fault_status_update_view`

#### 6.2.1 Create Fault Algorithm

The create operation begins when a user opens the fault creation page. The system first checks role permissions and prepares the input form. When the user submits the form, the backend validates the submitted data. If the validation is successful, the system assigns the current user as the reporting user, synchronizes closure fields based on the selected status, saves the new fault record to the database, creates an initial status history record, and redirects the user to the fault detail page.

Algorithm description:

1. User accesses the create fault page.
2. System verifies that the user role is allowed to create a fault.
3. System loads the fault input form.
4. User submits fault data.
5. System validates the form fields.
6. If valid, the system sets `reported_by` to the current user.
7. System calls closure synchronization logic.
8. System saves the fault record.
9. System creates an initial status history entry.
10. System redirects to the detail page.

#### 6.2.2 Read Fault Algorithm

The read operation consists of two levels: list-level retrieval and detail-level retrieval. In the list view, the system retrieves fault records and optionally applies filters such as status, severity, aircraft, and keyword search. In the detail view, the system retrieves a single fault record together with its related aircraft, assigned users, and status history.

Algorithm description:

1. User requests the fault list page or fault detail page.
2. System queries the database through the ORM.
3. For the list page, filters are applied if request parameters exist.
4. For the detail page, a single fault is retrieved by primary key.
5. Related objects are loaded using ORM relation handling.
6. Data is passed to the HTML template for rendering.

#### 6.2.3 Update Fault Algorithm

The update operation allows users to modify an existing fault record through the edit form. Before saving, the system validates whether the new status transition is allowed. If the workflow transition is valid, the updated data is saved, closure synchronization is applied, and a status history record is written if the status changes.

Algorithm description:

1. User opens the fault edit page.
2. System loads the selected fault record into the form.
3. User modifies fault data and submits the form.
4. System validates input fields.
5. System compares the old status and the new status.
6. System checks whether the transition is valid.
7. If valid, closure fields are synchronized.
8. System saves the updated fault record.
9. System creates a status history record when the status changes.
10. System redirects to the updated detail page.

#### 6.2.4 Delete Fault Algorithm

The delete operation is restricted to authorized roles. The system first displays a confirmation page. If the user confirms the action, the selected fault record is deleted from the database and the system redirects to the fault list page.

Algorithm description:

1. User opens the delete confirmation page.
2. System checks permission for deletion.
3. User confirms deletion.
4. System deletes the fault record.
5. System redirects to the fault list page.

#### 6.2.5 Workflow Update Algorithm

Besides conventional CRUD, the `faults` module also includes a workflow-specific update process. This process validates whether the requested next status is allowed according to the predefined transition rules. It can also update assignment data, analysis findings, root cause information, and resolution action depending on the selected workflow stage.

Algorithm description:

1. User opens the fault detail page.
2. User selects a new status and submits the workflow update form.
3. System checks whether the user is allowed to update the fault.
4. System validates the requested status transition.
5. System updates assignment data if provided.
6. System updates analysis, root cause, or resolution fields depending on the selected state.
7. System changes the current status.
8. System synchronizes closure information.
9. System saves the fault record.
10. System creates a status history entry with notes.

### 6.3 Aircraft Module CRUD Algorithm

The `aircraft` module is used to manage aircraft master data. In the current implementation, the module supports list, create, and update operations. These operations ensure that each fault record can be associated with a valid aircraft entry.

#### 6.3.1 Create Aircraft Algorithm

1. Authorized user opens the aircraft create page.
2. System displays the aircraft input form.
3. User enters aircraft data and submits the form.
4. System validates the input.
5. If valid, the system saves the aircraft record.
6. System redirects to the aircraft list page.

#### 6.3.2 Read Aircraft Algorithm

1. User opens the aircraft list page.
2. System queries aircraft records from the database.
3. System calculates summary statistics where needed.
4. Data is rendered in the list template.

#### 6.3.3 Update Aircraft Algorithm

1. Authorized user opens the aircraft update page.
2. System loads the selected aircraft record.
3. User modifies aircraft information.
4. System validates the input.
5. If valid, the system saves the updated aircraft record.
6. System redirects to the aircraft list page.

### 6.4 Accounts Module CRUD Algorithm

The `accounts` module handles authentication and administrative user management. In addition to login, register, and logout operations, the system provides CRUD-style user management for administrators.

#### 6.4.1 Create User Algorithm

1. Admin opens the user creation page.
2. System displays the user input form.
3. Admin enters username, profile role, and password.
4. System validates the input.
5. If valid, the system creates a `User` record.
6. System creates the corresponding `UserProfile` record.
7. System redirects to the user management page.

#### 6.4.2 Read User Algorithm

1. Admin opens the user management page.
2. System queries all users and their profile data.
3. Data is displayed in tabular format.

#### 6.4.3 Update User Algorithm

1. Admin opens the user update page.
2. System loads the selected user and profile data.
3. Admin modifies fields such as full name, role, and password.
4. System validates the input.
5. System saves the updated `User` and `UserProfile` records.
6. System redirects to the user management page.

#### 6.4.4 Delete User Algorithm

1. Admin selects a user for deletion.
2. System checks administrative authorization.
3. Admin confirms deletion.
4. System deletes the selected user record.
5. Related one-to-one profile data is removed through cascading behavior.

### 6.5 AI Module Operational Algorithm

Although the `ai_tools` module is not a conventional CRUD module, it represents an important operational algorithm in the system because it processes AI-assisted generation requests.

#### 6.5.1 Generate Description Algorithm

1. User enters aircraft, subsystem, severity, and flight phase data.
2. User clicks the AI generation button.
3. Frontend sends a request to the AI endpoint.
4. Backend validates that the required parameters are present.
5. System prepares an AI prompt.
6. System attempts to call the OpenRouter API.
7. If the external API succeeds, the generated description is returned.
8. If the external API is unavailable, the local fallback description builder is used.
9. The generated text is returned to the form interface.

#### 6.5.2 Explain Fault Algorithm

1. User opens the fault detail page.
2. User clicks the explain button.
3. Frontend sends a request to the explanation endpoint.
4. Backend loads the selected fault record and related aircraft data.
5. System constructs the explanation prompt from fault data.
6. System attempts to call the OpenRouter API.
7. If successful, the AI explanation is returned and stored in the fault record.
8. If unsuccessful, the fallback explanation builder generates a local explanation.
9. The result source is returned to the interface together with the generated explanation.

### 6.6 Suggested Algorithm Figure Labels

- Fault Creation Algorithm
- Fault Update and Workflow Validation Algorithm
- Aircraft Master Data Management Algorithm
- User Management Algorithm
- AI-Assisted Fault Description Generation Algorithm

## 7. Source Reference in the Actual Project

The content in this document is based on the implementation of:

- [accounts/models.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/accounts/models.py)
- [faults/models.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/faults/models.py)
- [faults/services.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/faults/services.py)
- [config/urls.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/config/urls.py)
- [accounts/urls.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/accounts/urls.py)
- [faults/urls.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/faults/urls.py)
- [aircraft/urls.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/aircraft/urls.py)
- [dashboard/urls.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/dashboard/urls.py)
- [reports/urls.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/reports/urls.py)
- [ai_tools/urls.py](c:/Program Files/Collage/De'Wei/Aircraft_Test_Fault_Django/ai_tools/urls.py)
