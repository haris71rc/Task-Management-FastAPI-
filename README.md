# Task Management FastAPI

A backend API for teams to register and log in, organize work into projects, create and manage tasks, upload task attachments, and receive background notifications.

Built with **FastAPI**.

---

## Features

| Area | Description |
|------|-------------|
| **Auth** | User registration and login with secure password hashing and JWT-based access |
| **Projects** | Create and manage team projects |
| **Tasks** | Create, update, assign, and track tasks within a project |
| **Attachments** | Upload and attach files to tasks |
| **Notifications** | Background jobs that notify users about task updates and assignments |

---

## Tech stack

- **FastAPI** — async REST API
- **Pydantic** — request/response validation
- **Uvicorn** — ASGI server
- Planned: database (SQLAlchemy + PostgreSQL), JWT auth, file storage, Celery/Redis for background notifications

---

## Project structure

```text
Task-Management-API/
├── app/
│   ├── main.py              # FastAPI application entrypoint
│   ├── schemas.py           # Pydantic models
│   └── api/
│       └── v1/
│           ├── router.py    # API v1 router
│           ├── health.py    # Health check
│           └── tasks.py     # Task endpoints
├── requirements.txt
└── README.md
```

---

## Getting started

### Prerequisites

- Python 3.11+
- `pip` (or your preferred package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/haris71rc/Task-Management-FastAPI-.git
cd Task-Management-FastAPI-

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- App: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative docs (ReDoc): [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API overview

Base path: `/api/v1`

### Currently available

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Service health check |
| `GET` | `/api/v1/{task_id}` | Fetch a task by ID |

### Planned endpoints

| Area | Examples |
|------|----------|
| **Auth** | `POST /api/v1/auth/register`, `POST /api/v1/auth/login` |
| **Projects** | `POST /api/v1/projects`, `GET /api/v1/projects`, `GET /api/v1/projects/{id}` |
| **Tasks** | `POST /api/v1/projects/{id}/tasks`, `PATCH /api/v1/tasks/{id}`, `DELETE /api/v1/tasks/{id}` |
| **Attachments** | `POST /api/v1/tasks/{id}/attachments`, `GET /api/v1/tasks/{id}/attachments` |
| **Notifications** | `GET /api/v1/notifications`, mark-as-read endpoints |

---

## Example health check

```bash
curl http://127.0.0.1:8000/api/v1/health
```

```json
{
  "status": "ok",
  "service": "task-management-api"
}
```

---

## Roadmap

- [x] Project scaffolding and health endpoint
- [ ] User registration & login (JWT)
- [ ] Project CRUD
- [ ] Task CRUD with assignment and status
- [ ] Task attachment uploads
- [ ] Background notification workers
- [ ] Tests and CI

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Open a pull request

---

## License

MIT
