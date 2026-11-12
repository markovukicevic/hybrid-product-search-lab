# Amazon ESCI — Product Search

An evaluated English product-search project. The Docker foundation and reproducible ESCI
data preparation are in place; no search endpoint is implemented and no quality claims
are made yet. Local raw/prepared data lives under the Git-ignored `data/` directory.

## Local Docker environment

Copy `.env.example` to `.env` and set a database password. Then:

```sh
docker compose up --build -d
docker compose ps
curl --fail http://localhost:8000/health/ready
```

Open http://localhost:5173 and API documentation at http://localhost:8000/docs.
All application services run in Docker. PostgreSQL is internal to Compose; web and API
ports bind to loopback. Database and model cache use persistent named volumes.
`docker compose down` preserves volumes; `down -v` deletes database and model data.
Changing the password in `.env` does not rotate an existing database volume's password.

Run checks inside the backend container:

```sh
docker compose run --rm --no-deps api ruff check .
docker compose run --rm --no-deps api pytest
```

Dependency versions are locked in `backend/uv.lock` and `frontend/package-lock.json`.
Docker builds use `uv sync --locked` and `npm ci`; regenerate locks with `uv lock` in
the backend Python 3.12 environment and `npm install --package-lock-only` in `frontend/`.
For data preparation, build with `compose.data.yaml`; that profile installs only the
locked pandas/PyArrow data dependencies. The separate research extra includes model and
evaluation dependencies. Its image build currently fails because `pytrec-eval-terrier`
needs a compiler absent from the base image, and the lock resolves CUDA/NVIDIA packages.
No model weights have been downloaded.

Model and evaluation dependencies remain optional. Upstream Parquet schemas and counts
are inspected and recorded in `docs/DATASET.md`; PostgreSQL schema and migrations await
the ingestion design. No automatic migration runs on API startup.

## Evaluation contract

Maintain separate judged-candidate ranking and full-catalog retrieval experiments.
Keep the official test split untouched. Derive validation from training query groups;
check query text and identifier overlap before splitting. Select whole queries and retain
all judgments for each selected query. Record source checksums, seeds and split manifests.
Upstream schema, counts, splits, and licensing have been inspected and are recorded in
[docs/DATASET.md](docs/DATASET.md):
https://github.com/amazon-science/esci-data

Document nDCG@10 gains and Recall@10 relevance thresholds before evaluation. Measure
p50/p95 latency with hardware, model revisions, warmup, concurrency and catalog size.
Report indexing time/storage and query compute costs, judgment coverage, error examples
and query slices. Unjudged products have unknown relevance. Local inference consumes
compute despite having no per-call API fee. Tune on validation only.

## Deployment direction

Target: a future markovu.com subdomain on a Netcup VPS. No deployment performed.
Compose avoids machine-specific paths. Add TLS/reverse-proxy configuration, production
secrets, resource sizing, backups and restoration checks before deployment.

## Reproducibility status

Dependency versions are recorded in `backend/uv.lock` and `frontend/package-lock.json`.
Docker builds use `uv sync --locked` and `npm ci`. Container image digests and model
revisions still need pinning before measured experiments.

See `PROGRESS.md` for verified state and blockers.
