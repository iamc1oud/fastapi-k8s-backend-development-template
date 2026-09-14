# backend

FastAPI + Piccolo ORM sample: `Task` CRUD backed by Postgres, k8s-ready.

## Layout

Django-style: each feature is a self-contained app under `src/apps/`, registered
in `piccolo_conf.py` and wired into the API in `src/backend/main.py`.

- `piccolo_conf.py` — Piccolo engine + app registry (like Django's `INSTALLED_APPS`)
- `src/backend/main.py` — FastAPI app factory, mounts each app's router
- `src/apps/<app>/models.py` — Piccolo `Table` classes
- `src/apps/<app>/schemas.py` — Pydantic request/response models (generated from tables)
- `src/apps/<app>/routes.py` — FastAPI router (like Django's `urls.py` + `views.py`)
- `src/apps/<app>/piccolo_app.py` — app config (name, migrations path, tables)
- `src/apps/<app>/piccolo_migrations/` — migrations, one folder per app (generate with the CLI, see below)

To add a new app: copy the `src/apps/tasks` layout, add its dotted path to
`APP_REGISTRY` in `piccolo_conf.py`, and include its router in `src/backend/main.py`.

## Setup

DB connection is env-driven (`src/backend/settings.py`): `DB_HOST`, `DB_PORT`,
`DB_NAME`, `DB_USER`, `DB_PASSWORD`. Point these at a Postgres instance
(a single SQLite file can't be shared across replicas/pods).

```bash
uv sync
uv run piccolo migrations forwards all
```

After changing an app's `models.py`, generate a new migration with the CLI (don't hand-write migration files):

```bash
uv run piccolo migrations new tasks --auto
uv run piccolo migrations forwards tasks
```

## Run

```bash
uv run fastapi dev src/backend/main.py
```

Endpoints: `GET/POST /tasks`, `GET/PATCH/DELETE /tasks/{id}`, `GET /healthz`
(liveness), `GET /readyz` (readiness, checks DB connectivity).

## Container

```bash
docker build -t backend:local .
```

Multi-stage build (`uv` resolves/installs in a builder stage, runtime image
is plain `python:3.13-slim`), runs as non-root, serves on `:8000`.

## Kubernetes deploy

Manifests are in `k8s/`. Migrations run as a one-shot Job, separate from the
app Deployment, so replicas never race each other applying schema changes:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml        # replace with your real secret manager in prod

# build/push your image, then point migrate-job.yaml and deployment.yaml at it
kubectl apply -f k8s/migrate-job.yaml
kubectl wait --for=condition=complete job/backend-migrate -n backend --timeout=120s
kubectl delete job/backend-migrate -n backend

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml           # requires metrics-server in the cluster
```

What makes it scale horizontally:
- **Postgres, not SQLite** — state is shared across pods instead of living in
  one pod's filesystem.
- **DB config from env/Secret** — no baked-in connection info, same image
  runs in any environment.
- **Connection pool per pod** (`lifespan` in `main.py`), not a new connection
  per request.
- **`/healthz` + `/readyz` probes** — kubelet restarts wedged pods, and only
  routes traffic to pods that can actually reach the DB.
- **Migrations as a separate Job** — schema changes apply once, before the
  rolling update, instead of N replicas fighting over `ALTER TABLE`.
- **HPA on CPU** — replica count reacts to load instead of being fixed.

Verified locally end-to-end with `kind` + a Postgres pod: 3 replicas roll out
healthy, the Service load-balances across them, and a task created via one
pod is immediately visible from all others.
