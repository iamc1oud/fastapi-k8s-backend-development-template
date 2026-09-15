# Load testing (k6)

Requires the app running (locally, via `docker compose up`, or against a
deployed cluster) and k6 (or Docker, no local install needed).

## Smoke test

Fast sanity check: 2 VUs, 10s, hits `/healthz`, `/readyz`, `/tasks`.

```bash
docker run --rm -i -e BASE_URL=http://host.docker.internal:8000 grafana/k6 run - < benchmark/smoke.js
```

## Full load test

Ramps 20 -> 50 VUs over ~3.5 minutes, exercises the whole `Task` CRUD flow
(create, list, get, update, delete). Thresholds fail the run if p95 exceeds
200ms (list/create/get) or the overall p99 exceeds 500ms, or error rate > 1%.

```bash
docker run --rm -i -e BASE_URL=http://host.docker.internal:8000 grafana/k6 run - < benchmark/tasks.js
```

Point at a different target (deployed cluster, staging, etc):

```bash
docker run --rm -i -e BASE_URL=http://backend.example.com grafana/k6 run - < benchmark/tasks.js
```

On Linux, `host.docker.internal` may not resolve — use `--network host` and
`BASE_URL=http://localhost:8000` instead. If you have k6 installed locally,
skip Docker entirely: `k6 run benchmark/tasks.js`.

## Dashboard / HTML report

k6 has a built-in web dashboard: a live view during the run, plus an HTML
report written to disk after it finishes (needs a run of ~40s+ — shorter
runs don't have enough sampled periods and the export is silently skipped,
so `smoke.js`'s default 10s won't produce one).

```bash
mkdir -p benchmark/reports
docker run --rm -i \
  -e BASE_URL=http://host.docker.internal:8000 \
  -e K6_WEB_DASHBOARD=true \
  -e K6_WEB_DASHBOARD_EXPORT=/reports/report.html \
  -p 5665:5665 \
  -v "$(pwd)/benchmark/reports:/reports" \
  grafana/k6 run -o web-dashboard - < benchmark/tasks.js
```

- Live dashboard while it runs: http://localhost:5665
- After it finishes: open `benchmark/reports/report.html` in a browser.

`benchmark/reports/` is gitignored — reports are a local artifact, not
something to commit.
