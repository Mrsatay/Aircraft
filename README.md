# Aircraft Test Fault Django

Django version of the Aircraft Test Fault Management System, migrated from the Java Servlet/JSP implementation to a simpler stack for further development and a more stable demo.

## How to Run

```powershell
cd "c:\Program Files\Collage\De'Wei\Aircraft_Test_Fault_Django"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/demo_data.json
python manage.py runserver
```

Then open `http://127.0.0.1:8000/accounts/login/`.

## Notes

- This project is configured to use PostgreSQL by default.
- Database configuration is read from these environment variables:
  `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- To enable AI through OpenRouter, set the `OPENROUTER_API_KEY` environment variable. If it is not configured, the application uses the local fallback.
- CSS, JS, Bootstrap, Bootstrap Icons, Chart.js, and Font Awesome assets were copied from the Java project.
- Functional modules: login, registration, dashboard, fault list, fault creation, fault detail, aircraft management, reports, user management, workflow status history, and AI helper endpoint.
- The AI feature uses a local fallback when `OPENROUTER_API_KEY` is not configured.
- The demo dataset with 100 faults is stored in `fixtures/demo_data.json`. Run `python manage.py loaddata fixtures/demo_data.json` after `migrate` to populate a new database.
- If you use the demo data and do not know the login password, reset the admin account password with `python manage.py changepassword admin`.

## Verification

```powershell
python manage.py test
```

All core application tests are currently prepared for the `accounts`, `aircraft`, `faults`, `reports`, and `ai_tools` modules.

## Migrating Data from an Old SQLite Database

If this project previously used `db.sqlite3` and has now moved to PostgreSQL, you can migrate the old data with this command:

```powershell
python manage.py import_sqlite_data --sqlite-path db.sqlite3 --flush
```

Use `--flush` when the target PostgreSQL database already has data and you want to replace it with the SQLite contents.
