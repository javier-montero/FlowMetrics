# FlowMetrics

## Seed the database

Start the stack with `docker compose up --build`, then run the seed command:

```sh
docker compose exec backend python -m app.seed
```

The command creates the `metrics` table and inserts example metrics only when
they do not already exist. It is safe to run more than once. Edit
`backend/app/seed.py` to customize the starter data. NOTE: this is just a placeholder.
