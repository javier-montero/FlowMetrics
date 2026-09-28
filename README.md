# FlowMetrics

## Seed the database

Start the stack with `docker compose up --build`, then run the seed command:

```sh
docker compose exec backend python -m app.seed
```

The command creates the database tables and inserts a small RunScope fixture:
one completed run, one active run, their samples and process executions, and
matching SLURM job records. Existing records are left unchanged, so the command
is safe to run more than once. Edit `backend/app/seed.py` to customize the
deterministic starter data.
