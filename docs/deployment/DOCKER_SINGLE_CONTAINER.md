```markdown
DOCKER SINGLE-CONTAINER (experimental)
=====================================

Warning: this is an experimental single-container image that runs both the Django web app and a PostgreSQL server in the same container. This is NOT recommended for production. Use this only for demos or ephemeral testing. For production, prefer a web-only container + managed database.

Files added
- `Dockerfile` — builds an image with Python and PostgreSQL server installed.
- `docker-entrypoint.sh` — initializes DB (first run), starts Postgres, runs migrations and collectstatic, then execs the container CMD (Gunicorn).
- `.dockerignore` — reduce build context.

Environment variables (example defaults used by the image)
- `POSTGRES_DB` (default: `postgres`)
- `POSTGRES_USER` (default: `postgres`)
- `POSTGRES_PASSWORD` (default: `postgres`) — strongly set this in production/testing!
- `POSTGRES_PORT` (default: `5432`)
- `DATABASE_URL` (optional) — if set, entrypoint will not override it. If not set, entrypoint will set it to the local Postgres instance.

Build locally

PowerShell (build tag with your Docker Hub username):
```powershell
docker build -t <dockerhub-username>/alx-ecommerce:experimental .
```

Push to Docker Hub
```powershell
docker login
docker push <dockerhub-username>/alx-ecommerce:experimental
```

Run locally (recommended flags)

Create a named volume for Postgres data so container restarts preserve DB:
```powershell
docker volume create alx_pgdata
```

Run the container with ports mapped and env vars set:
```powershell
docker run -d --name alx-ecommerce -p 8000:8000 -p 5432:5432 \
  -e POSTGRES_DB=alxdb -e POSTGRES_USER=alxuser -e POSTGRES_PASSWORD=StrongPassword123 \
  -v alx_pgdata:/var/lib/postgresql/data \
  <dockerhub-username>/alx-ecommerce:experimental
```

Notes:
- The `docker-entrypoint.sh` script will initialize the Postgres data directory at `/var/lib/postgresql/data` on first run, create the specified DB and user, then start Postgres.
- The entrypoint will automatically set `DATABASE_URL` to the local Postgres instance if not already provided (useful for Django `django-environ`).
- The container runs Gunicorn on port `8000`.

Deploying to Render (experimental, caution)
- Render and many PaaS systems expect one main process per container. Running two services in one container (Postgres + app) may work but is fragile.
- If you still want to deploy this to Render: create a Web Service using a Dockerfile, and attach a persistent disk to store `/var/lib/postgresql/data`. In Render's UI you'll:
  - Choose "Docker" as the environment and point at your repo or image.
  - Set required environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).
  - Add a persistent disk and mount it to `/var/lib/postgresql/data`.

Production recommendation
- Use a web-only Docker image (no DB) and a managed Postgres instance (Render Postgres, AWS RDS, DigitalOcean Managed DB, etc.). This is more secure, scalable and reliable.
