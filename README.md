# CampusFlow Student Management System

A Django-based college administration application with role-scoped student and faculty access, academic records, attendance, analytics, and report exports.

## Exact project structure

```text
.
├── accounts/
│   ├── migrations/          Custom user schema
│   ├── admin.py             User administration
│   ├── forms.py             Sign-in and password forms
│   ├── models.py            Role-aware Django user
│   ├── permissions.py       Admin and staff access mixins
│   ├── tests.py             Authentication and role-access tests
│   ├── urls.py              Sign-in, sign-out, password routes
│   └── views.py             Authentication views
├── academics/
│   ├── migrations/          Academic schema and constraints
│   ├── admin.py             Academic model administration
│   ├── forms.py             Department, course, semester, subject, marks forms
│   ├── models.py            Department, course, semester, subject, mark
│   ├── tests.py             Grade, validation, access tests
│   ├── urls.py              Academic management routes
│   └── views.py             CRUD and results workflows
├── attendance/
│   ├── migrations/          Attendance schema and unique constraint
│   ├── admin.py             Attendance administration
│   ├── forms.py             Subject-scoped attendance validation
│   ├── models.py            Present, absent and leave records
│   ├── tests.py             Attendance workflow tests
│   ├── urls.py              Daily records, edits, history, analytics
│   └── views.py             Attendance operations and monthly data
├── config/
│   ├── asgi.py
│   ├── settings.py          Environment, security, database configuration
│   ├── urls.py              Root URL routing
│   └── wsgi.py
├── faculty/
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py             Faculty creation and update validation
│   ├── models.py            Faculty profile
│   ├── urls.py
│   └── views.py
├── reports/
│   ├── dashboard_urls.py
│   ├── tests.py             Dashboard and PDF/XLSX export tests
│   ├── urls.py
│   └── views.py             Dashboard, analytics and downloads
├── students/
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py             Enrollment and department/course validation
│   ├── models.py            Student profile and generated ID
│   ├── urls.py
│   └── views.py             Search, filters and profile pages
├── static/
│   ├── css/app.css          Responsive visual design
│   └── js/app.js            Mobile sidebar behavior
├── templates/
│   ├── accounts/login.html
│   ├── attendance/
│   │   ├── analytics.html
│   │   ├── history.html
│   │   └── list.html
│   ├── faculty/list.html
│   ├── reports/
│   │   ├── dashboard.html
│   │   └── index.html
│   ├── shared/
│   │   ├── base.html
│   │   ├── confirm_delete.html
│   │   ├── form.html
│   │   ├── list.html
│   │   ├── pagination.html
│   │   └── resource_list.html
│   └── students/detail.html
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

Each application keeps its models, forms, views, routes, admin registration, and migrations together; shared layout and static assets are centralized.

### Database relationships

- A department owns courses; student and faculty profiles each belong to a department.
- A course has semesters and subjects. Each subject belongs to one course and semester and can be assigned to a faculty member.
- A student belongs to one course and has a generated unique student ID.
- Attendance is unique per student, subject, and date.
- A mark is unique per student, subject, and semester; marks are validated against the subject/course and semester.
- `accounts.User` extends Django authentication users with `ADMIN` and `FACULTY` roles.

SQLite is the default database. PostgreSQL can be selected with `DJANGO_DB_ENGINE=postgresql` and the `POSTGRES_*` environment variables. `requirements.txt` includes the PostgreSQL driver.

## Setup

Run these commands from the project directory in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `DJANGO_SECRET_KEY` in `.env` to a private random value before deployment. `DJANGO_DEBUG=True` is intended only for local development. For production, set `DJANGO_DEBUG=False`, set `DJANGO_ALLOWED_HOSTS`, use HTTPS, and configure a production secret key.
When HTTPS is fully deployed, configure `DJANGO_SECURE_HSTS_SECONDS` (for example `31536000`) to enable HSTS; enable subdomain/preload flags only if every affected host is HTTPS-ready.

## Database setup and administrator

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

The superuser is automatically assigned the Administrator role. The Django admin interface is available at `/django-admin/`. Alternatively, add faculty accounts from the Faculty page; faculty accounts should change their temporary password after signing in.

## Run and test

```powershell
python manage.py runserver
python manage.py check
python manage.py test
```

Open `http://127.0.0.1:8000/` and sign in. The dashboard links to student, faculty, academic, attendance, and report modules. Use Django admin or the application pages to create departments, courses, semesters, subjects, and faculty assignments before enrolling students and recording attendance or marks.

## Module walkthrough and implementation steps

1. **Foundation and database** — `config/` sets up Django and the database; `accounts/models.py`, `academics/models.py`, `students/models.py`, `faculty/models.py`, and `attendance/models.py` define linked records, constraints, and validation. Run `makemigrations` and `migrate` before starting the server.
2. **Accounts and roles** — `accounts/` provides Django sign-in/sign-out, password changes, and permission mixins. The superuser is Administrator; faculty have read access to assigned students/subjects and can write attendance/marks only for assigned subjects.
3. **Student management** — `students/` provides validated enrollment, generated IDs, directory search/filtering, profiles, and administrator-only edits/deletions.
4. **Faculty management** — `faculty/` creates faculty login accounts and profiles, validates unique account identifiers, and supports department-wise listing and profile updates.
5. **Academic management** — `academics/` provides CRUD for departments, courses, semesters, and subjects; subject assignments; marks entry; and calculated grades.
6. **Attendance management** — `attendance/` provides dated present/absent/leave records, one record per student/subject/day, filters, corrections, student history, and monthly analytics.
7. **Dashboard and reports** — `reports/` renders enrollment/performance/attendance metrics and Chart.js charts, with PDF/XLSX downloads. Faculty data is restricted to assigned courses/subjects.

Each module is available from the authenticated sidebar. Verify the integrated modules with `python manage.py test`; the suite covers roles, records, dashboard rendering, and both export formats.

All write forms use Django model/form validation and CSRF tokens. Use the Django test suite after changes to validate database and access-control behavior.
