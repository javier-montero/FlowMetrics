# FlowMetrics

## Frontend development

Open the project in VS Code and run **Dev Containers: Reopen in Container** from
the Command Palette. VS Code attaches to the frontend container, where the
workspace TypeScript compiler and React dependencies are installed. The database
and backend services start alongside it.

## Backend layout

```text
backend/
└── app/
	├── routes/
	├── db/
	├── models/
	├── schemas/
	├── services/
	└── seed/
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

Start the stack with `docker compose up --build`, then run the seed command:

```sh
docker compose exec backend python -m app.seed
```

By default, the seeder creates 32 synthetic runs balanced across 24-, 48-,
96-, and 384-well plates, with queued, running, completed, failed, and cancelled
runs distributed across workflow steps. Faker and a fixed random seed make
generated random details reproducible; timestamps are relative to seeding time.
Change the run count or seed with
`docker compose exec backend python -m app.seed --runs 40 --seed 1234`.
Existing generated records are left unchanged, so rerunning with the same seed
is safe; increasing the count adds records. Well positions are included in
sample IDs, such as `SIM-42042-0001-A01`.
