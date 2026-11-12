# Development handover

## 2026-11-12 — Foundation scaffold

Workspace verified writable and initially empty. Created Compose configuration,
FastAPI health endpoints, React/TypeScript shell, environment template and evaluation
contract. No ingestion or model downloads performed.

Blockers:
- Docker client exists, but daemon socket access is denied at
  `/Users/markovu/.docker/run/docker.sock`. No socket permissions changed.
- Account usage tool failed. The requested stop at 20% of the five-hour allowance
  cannot be reliably enforced. No usage figure is known.

Foundation remains incomplete until containers build/start, checks run in Docker,
frontend lockfile and uv.lock exist, and health checks pass. Next inspect the official
ESCI source schema, counts, splits and licensing before ingestion and migrations.

Approved stages: foundation → ingestion/validation/sampling → PostgreSQL FTS →
embeddings → RRF hybrid → reranking → comparison UI and portfolio report.

Verified without the daemon: Python files parse; pyproject TOML and frontend JSON
parse; `docker compose config --quiet` passes with a temporary validation password.
Frontend lockfile generation did not finish and was interrupted. No dependency install,
container build, Ruff/pytest run or UI runtime verification is claimed.
Usage checker retried at checkpoint and failed again; stopped at foundation scaffold.

## 2026-11-12 — Continued without Docker access

User asked to continue without resolving execution permissions.
- Inspected upstream README, LICENSE and NOTICE; recorded schema and published
  English ranking counts in docs/DATASET.md. Actual Parquet files not downloaded.
- Added deterministic query splitting/sampling, normalized-text overlap quarantine,
  official test preservation, and complete candidate retention.
- Added preparation CLI for local source Parquet files, source checksums, schema and
  counts manifest, full US catalog output, and validation of catalog references.
- Added opt-in research Compose build with pandas/PyArrow/model dependencies.
- Four dependency-free dataset tests passed on host Python; these are utility tests,
  not application services. Docker services remain unrun. Preparation CLI only syntax
  checked; no real data ingestion, database integration or metrics claimed.
- Usage checker failed again; 20% account allowance remains unobservable.
Next: restore Docker execution, lock dependencies, inspect physical source Parquet
and verify preparation against it, then implement migrations and PostgreSQL FTS.


## 2026-11-12 — Foundation verified locally

- Added `backend/uv.lock` and `frontend/package-lock.json`; backend Dockerfile installs
  with `uv sync --locked`, frontend uses `npm ci`.
- Rebuilt both service images successfully. TypeScript and Vite production build passed.
- Started PostgreSQL/pgvector, API and frontend in Docker Compose using a temporary
  verification password. `/health/live` returned `{"status":"ok"}`, `/health/ready`
  returned `{"status":"ready"}`, and frontend HTML was served on loopback. The browser
  interface was not visually inspected. Services remain running; no deployment performed.
- Ruff passed. Pytest: 6 passed, with one Starlette/httpx deprecation warning. Fixed one
  Ruff line-length issue in `backend/app/dataset.py`.
- Lock dry-run including research extras resolved 97 packages. It includes large
  CUDA/NVIDIA dependencies; research image size and CPU-only packaging need evaluation.
- Usage checker last reported 6% of the five-hour allowance.

Still pending: real ESCI download/schema inspection and preparation run; research image
build/model downloads; PostgreSQL schema/migrations/ingestion and search implementation.
No search quality, latency or cost results exist.


## 2026-11-12 — ESCI data preparation verified

- Pinned upstream `amazon-science/esci-data` to actual main commit
  `7916cdf6ab75a462e77f20ab40428a10923998d5`; downloaded both Parquet files and
  preserved upstream LICENSE/NOTICE in ignored `data/raw/`. SHA-256 values, byte sizes,
  source URLs, physical schemas and row counts are recorded in the output manifest.
- PyArrow physical inspection: examples 2,621,288 rows (including upstream
  `__index_level_0__` field); products 1,814,924 rows. Files total 1,160,144,273 bytes.
- Measured US `small_version=1` counts match upstream: train 20,888 queries / 419,653
  judgments; test 8,956 / 181,701. Full pinned US catalog: 1,215,854 products.
- Successful prepared output: `data/prepared/run-2026-11-12-seed42-cap100-provenance/`
  (731 MB compressed). Seed 42; cap 100 train and validation queries each; official test
  untouched; full catalog retained. Output: train 100/2,039 judgments, validation
  100/1,962, test 8,956/181,701, quarantine 0, catalog 1,215,854.
- Deterministic manifest replay, per-query candidate-count retention, source checksums,
  official counts, full test/catalog counts, and normalized query-text leakage checks
  passed.
- Added a locked pandas/PyArrow `data` extra and `compose.data.yaml` with a separate image
  tag so preparation avoids loading model/evaluator dependencies. Ruff passed; pytest 6
  passed (one Starlette/httpx deprecation warning).
- Full research image build remains blocked: `pytrec-eval-terrier` requires a compiler
  absent from the base image; its dependency lock also includes large CUDA/NVIDIA wheels.
  No model weights were downloaded.
- Usage checker last reported 8% of the five-hour allowance.

Still pending: resolve research/evaluation image packaging; use the prepared corpus for
schema/migrations, PostgreSQL ingestion, FTS and later retrieval/evaluation stages.
No search quality, latency or cost results exist.
