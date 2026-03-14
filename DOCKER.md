# Docker Setup

This project is containerized with Docker Compose.

## Services

- `backend`: FastAPI app on internal Docker network port `8000`
- `frontend`: Nginx serving built frontend on port `5173`

Frontend API requests are routed through Nginx from `/api/*` to the backend service.

## Run

From repository root:

```bash
docker compose up --build
```

Open:

- Frontend: `http://localhost:5173`
- Backend API docs (proxied): `http://localhost:5173/api/docs`

## Stop

```bash
docker compose down
```

## Data persistence

SQLite database is persisted in Docker volume `backend_data` at `/app/data/app.db` in the backend container.
