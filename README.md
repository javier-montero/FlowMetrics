# FlowMetrics

## Architecture

```mermaid
flowchart LR
    Browser[Browser]
    Frontend[React and TypeScript<br/>Vite on port 5173]
    Backend[FastAPI Application<br/>Gunicorn on port 8000]
    Database[(PostgreSQL 16<br/>port 5432)]
    Compose[Docker Compose]

    Browser --> Frontend
    Frontend -->|HTTP via JSON| Backend
    Backend --> |SQLAlchemy ORM| Database
    Compose -. runs .-> Frontend
    Compose -. runs .-> Backend
    Compose -. runs .-> Database
```

## Infrastructure

- **Frontend:** Node 22 Alpine container serving the Vite development server on port `5173`.
- **Backend:** Python 3.12 container running FastAPI through Gunicorn and Uvicorn workers on port `8000`.
- **Database:** PostgreSQL 16 Alpine on port `5432`, persisted in the `postgres_data` volume.

## Dependencies

**Backend** dependencies are managed in `backend/requirements.txt`:

- FastAPI, Gunicorn, and Uvicorn worker
- SQLAlchemy and Psycopg 3
- Faker for seedign data

**Frontend** dependencies are managed in `frontend/package.json` and locked in `frontend/package-lock.json`:

- React 19 and TypeScript
- Vite 7 and the React Vite plugin
- Bootstrap 5 and Bootstrap Icons
- PrimeReact and PrimeIcons for specialized widgets

## Backend directories

```text
backend/
└── app/
    ├── db/
    ├── models/
    ├── routes/
    ├── schemas/
    ├── seed/
    └── services/
```

## Frontend directories

```text
frontend/
└── src/
    ├── app/
    ├── features/
    ├── lib/
    └── styles/
```

## Database schema

```mermaid
erDiagram
    WORKFLOW_DEFINITIONS {
        int id PK
        string name
        string version
    }

    PROCESS_DEFINITIONS {
        int id PK
        int workflow_id FK
        string name
        int expected_duration_seconds
        int sort_order
    }

    RUNS {
        int id PK
        string run_id UK
        int workflow_id FK
        string status
        int sample_count
        datetime started_at
        datetime completed_at
        int tat_seconds
        int expected_tat_seconds
        int tat_variance_seconds
        string sequencer
        string current_step
        float progress_percent
        int failed_task_count
        int retried_task_count
    }

    SAMPLES {
        int id PK
        int run_id FK
        string sample_id UK
        string status
    }

    PROCESS_EXECUTIONS {
        int id PK
        string task_id UK
        int run_id FK
        int process_id FK
        string sample_id FK
        string status
        datetime submitted_at
        datetime started_at
        datetime completed_at
        int queue_time_seconds
        int execution_time_seconds
        int cpu_count
        float cpu_utilization_percent
        float memory_requested_mb
        float peak_memory_mb
        int exit_code
        int attempt
    }

    SLURM_JOBS {
        int id PK
        string job_id UK
        int process_execution_id FK
        string status
        datetime submitted_at
        datetime started_at
        datetime completed_at
        int requested_cpus
        float requested_memory_mb
        float peak_memory_mb
        int exit_code
        string node_list
    }

    WORKFLOW_DEFINITIONS ||--o{ PROCESS_DEFINITIONS : defines
    WORKFLOW_DEFINITIONS ||--o{ RUNS : has
    RUNS ||--o{ SAMPLES : contains
    RUNS ||--o{ PROCESS_EXECUTIONS : records
    PROCESS_DEFINITIONS ||--o{ PROCESS_EXECUTIONS : describes
    SAMPLES o|--o{ PROCESS_EXECUTIONS : runs_for
    PROCESS_EXECUTIONS ||--o{ SLURM_JOBS : schedules
```

## Seed the database

Start the stack:

```sh
docker compose up --build
```

In another terminal (or detach the current terminal), seed the database:

```sh
docker compose exec backend python -m app.seed
```

By default, this creates 32 synthetic runs balanced across 24-, 48-, 96-, and
384-well plates, with queued, running, completed, failed, and cancelled runs.
The fixed default seed (`42042`) makes generated random details reproducible;
timestamps are relative to seeding time.

Set a different run count or seed with:

```sh
docker compose exec backend python -m app.seed --runs 40 --seed 1234
```

Existing generated records are left unchanged. Rerunning with the same seed is
safe; increasing the run count adds records. Sample IDs include well positions,
such as `SIM-42042-0001-A01`.