# Backend Docker usage

## Standalone image

Build the ASGI-ready image from the `backend/` folder:

```bash
docker build -t fidelidade-backend-prod .
```

The image:

- installs all Python dependencies
- runs database migrations and `collectstatic` on startup
- serves the project via Daphne on `0.0.0.0:8000`

Run it by passing the `.env` file (or individual vars) plus any needed volumes:

```bash
docker run --env-file ./backend/.env -p 8000:8000 fidelidade-backend-prod
```

## docker-compose stack

A ready-to-run stack (Django, Postgres and Redis) lives at the repository root:

```bash
docker compose up --build backend
```

What it does:

- Loads variables from `backend/.env` but overrides the DB/Redis hosts for the containers.
- Provisions Postgres 16 + Redis 7 with persistent named volumes.
- Persists Django `media` and collected `staticfiles` under Docker volumes (`media_data` and `static_data`).

Use `docker compose up -d` to run in the background and `docker compose logs -f backend` to inspect server output. Update `ALLOWED_HOSTS`, JWT, and database credentials in `backend/.env` (or pass overrides) before deploying to a public environment.
