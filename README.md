# Task Manager (Django + Docker + CI/CD)

A production-ready Task Manager built with Django and PostgreSQL, containerized with Docker, and deployed using GitHub Actions.

## Features

- User authentication (register, login, logout)
- Task CRUD
- Project, Task, Tag, Comment models
- Many-to-one and many-to-many model relationships
- Django admin panel
- Redis cache/session support
- Separate Docker setup for development and production
- Automated CI/CD pipeline (test, build, push, deploy)

## Tech Stack

- Python 3.12
- Django
- PostgreSQL
- Redis
- Nginx
- Gunicorn
- Docker + Docker Compose
- GitHub Actions

## Project Structure

```text
config/                     # Django project settings/urls
tasks/                      # Main app (models, views, forms, tests)
templates/                  # HTML templates
docker/entrypoint.sh        # App startup script
nginx/nginx.conf            # Nginx config
docker-compose.yml          # Production stack
docker-compose.dev.yml      # Development stack
.github/workflows/deploy.yml # CI/CD workflow
scripts/deploy.sh           # Remote deploy script
```

## Setup

### 1. Local (without Docker)

1. Create and activate virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Configure `.env` in project root.

4. Run migrations and start server:
```powershell
python manage.py migrate
python manage.py runserver
```

### 2. Development (Docker)

Run development stack (`web + db + redis`) with hot reload:

```powershell
docker compose -f docker-compose.dev.yml up --build
```

Stop:
```powershell
docker compose -f docker-compose.dev.yml down
```

App URL:
- `http://127.0.0.1:8000/`

### 3. Production (Docker)

Run production stack (`nginx + web + db + redis`):

```powershell
docker compose up --build -d
```

Stop:
```powershell
docker compose down
```

App URL:
- `http://127.0.0.1/`

## Environment Variables

Create `.env` file in project root:

```env
DEBUG=False
TESTING=False
SECRET_KEY=replace_with_strong_secret
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost

DB_NAME=cloud_db
DB_USER=cloud_user
DB_PASSWORD=cloud_pass_123
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/1
```

Notes:
- Use strong `SECRET_KEY` in production.
- Add server IP/domain to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.

## Database Seed

Populate demo data:

```powershell
python manage.py seed_data
```

Reset task/comment demo data:

```powershell
python manage.py seed_data --reset
```

Inside Docker:

```powershell
docker compose exec web python manage.py seed_data
```

## Tests

Run tests locally:

```powershell
python -m pytest -q
```

Current suite includes 7 tests (auth, permissions, CRUD, comments, relationships).

## Docker Compose Commands (Quick Reference)

Production:

```powershell
docker compose up --build -d
docker compose ps
docker compose logs -f
docker compose down
```

Development:

```powershell
docker compose -f docker-compose.dev.yml up --build
docker compose -f docker-compose.dev.yml ps
docker compose -f docker-compose.dev.yml logs -f
docker compose -f docker-compose.dev.yml down
```

## CI/CD (GitHub Actions)

Workflow file:
- `.github/workflows/deploy.yml`

Trigger:
- On push to `main`
- Manual run (`workflow_dispatch`)

Pipeline steps:
1. Install dependencies
2. Run `black --check .`
3. Run `pytest`
4. Build Docker image
5. Push image to Docker Hub (`latest` + commit SHA tag)
6. SSH deploy to server
7. Run migrations
8. Collect static files
9. Restart services

Required GitHub Secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `SSH_PRIVATE_KEY`
- `SSH_HOST`
- `SSH_USERNAME`

## Deployment Notes

- Server app path expected by deploy script: `~/cloud`
- Deploy script: `scripts/deploy.sh`
- Main service image: `${DOCKERHUB_USERNAME}/cloud-web`

## Admin Access

Create superuser:

```powershell
python manage.py createsuperuser
```

Inside Docker:

```powershell
docker compose exec web python manage.py createsuperuser
```

Admin URL:
- `/admin/`
