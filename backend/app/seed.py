from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Metric

SEED_METRICS = [
    {"name": "requests_total", "value": 120.0},
    {"name": "active_users", "value": 24.0},
    {"name": "error_rate", "value": 0.02},
]


def seed():
    Base.metadata.create_all(bind=engine)

    with SessionLocal.begin() as session:
        existing_names = set(session.scalars(select(Metric.name)))
        new_metrics = [
            Metric(**metric)
            for metric in SEED_METRICS
            if metric["name"] not in existing_names
        ]
        session.add_all(new_metrics)

    print(f"Inserted {len(new_metrics)} metric(s).")


if __name__ == "__main__":
    seed()