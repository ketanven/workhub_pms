# WorkHub Backend

WorkHub is a Django + DRF backend for a freelancer work management system.
It now includes end-to-end modules for authentication, management, workbench time tracking, invoicing, analytics, reporting, productivity scoring, client trust, calendar, kanban, notifications, files, and workspace settings.

## What Is Implemented

### Auth and Identity
- Admin auth and profile flows
- User auth and profile flows
- JWT-based protected APIs (middleware-based auth guards)

### Management
- Clients CRUD
- Projects CRUD
- Tasks CRUD
- Project-specific task listing/creation

### Workbench (Time Tracking)
- Overview, project/task picker, active timer restore
- Timer lifecycle: start, pause, resume, break start/stop, stop
- Manual time entries
- Time entries listing, patch, delete
- Offline sync batch ingest

### Analysis
- KPI summary
- Web analytics series
- Earnings trend
- Time allocation split
- Top clients
- Task accuracy
- Invoice health
- Analysis export dataset endpoint

### Invoicing
- Invoice list/create/update/detail
- Create invoice from time entries
- Submit/send/reminder/mark-paid actions
- Payment add/list
- Invoice PDF endpoint
- Invoice stats
- Smart numbering config + next preview
- Invoice version history + restore

### Reporting
- Earnings report
- Time allocation report
- Project performance report
- Client analytics report
- Monthly bundle
- Report export job endpoint

### Productivity
- Productivity summary
- Weekly trend
- Task variance
- On-time rate
- Utilization
- Rules update

### Client Trust
- Trust summary
- Client trust list
- Per-client trust history
- Trust recalculation
- Rules update
- Risk alerts

### Calendar
- Event list/create/detail/update/delete
- Task feed
- Invoice feed

### Kanban
- Boards list/create/detail/update/delete
- Column create/update/delete
- Card create/update/delete/move

### Common Platform APIs
- Notifications list + mark read
- File upload + file metadata
- Workspace settings get/update
- Health endpoint

## Tech Stack
- Python 3.10+
- Django 4.2.x
- Django REST Framework
- MySQL

## Project Structure

```text
workhub/
├── common/
│   └── responses.py
├── core/
│   ├── controllers/
│   │   ├── Admin/
│   │   └── User/
│   ├── services/
│   │   ├── Admin/
│   │   └── User/
│   ├── serializers/
│   │   ├── Admin/
│   │   └── User/
│   ├── models/
│   │   ├── user.py, admin.py, client.py, project.py, task.py
│   │   ├── workbench.py
│   │   ├── invoicing.py
│   │   ├── operations.py
│   │   ├── calendar_kanban.py
│   │   └── platform.py
│   ├── management/
│   │   ├── commands/
│   │   └── seeders/
│   ├── migrations/
│   └── urls/
├── workhub/
│   ├── settings.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

## Request Flow

```text
Request -> Controller -> Serializer -> Service -> Model -> DB
                                   -> common ApiResponse
```

## Setup

### 1) Create environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure `.env`

```env
DEBUG=True
SECRET_KEY=your-secret-key

DB_NAME=workhub_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306

ALLOWED_HOSTS=127.0.0.1,localhost
LANGUAGE_CODE=en-us
TIME_ZONE=Asia/Kolkata
```

### 3) Run migrations

```bash
python3 manage.py migrate
```

### 4) Start server

```bash
python3 manage.py runserver
```

## Routing Overview

- Base prefix: `/api/`
- Admin routes: `/api/admin/...`
- User routes: `/api/user/...`

Examples:
- `/api/user/workbench/overview/`
- `/api/user/invoices/`
- `/api/user/calendar/events/`
- `/api/user/kanban/boards/`

## Seeding (Important)

Two seed commands are available.

### A) Management-only seed
Seeds client/project/task demo data.

```bash
python3 manage.py seed_management_data --module all
python3 manage.py seed_management_data --module clients
python3 manage.py seed_management_data --module projects
python3 manage.py seed_management_data --module tasks
```

### B) Full dashboard seed
Seeds all modules with linked demo data.

```bash
python3 manage.py seed_dashboard --module all
```

Or module-wise:

```bash
python3 manage.py seed_dashboard --module workbench
python3 manage.py seed_dashboard --module invoicing
python3 manage.py seed_dashboard --module analysis
python3 manage.py seed_dashboard --module reports
python3 manage.py seed_dashboard --module productivity
python3 manage.py seed_dashboard --module trust
python3 manage.py seed_dashboard --module calendar
python3 manage.py seed_dashboard --module kanban
python3 manage.py seed_dashboard --module platform
```

### Demo user
- Email: `demo@workhub.com`
- Password: `password123`

## Migration Notes

Current migration chain includes:
- `0001` to `0004`: auth/client/project/task base
- `0005` to `0009`: workbench, invoicing, operations, calendar/kanban, platform models

Useful commands:

```bash
python3 manage.py showmigrations core
python3 manage.py makemigrations core
python3 manage.py migrate
```

## API Testing Tips

- Always send user auth token for protected `/api/user/...` endpoints:

```http
Authorization: Bearer <access_token>
```

- Use Postman collection/folders module-wise:
  - Workbench
  - Analysis
  - Invoicing
  - Reports
  - Productivity
  - Client Trust
  - Calendar
  - Kanban

## Status

Backend is ready for frontend integration with seeded demo data support for UI validation.
