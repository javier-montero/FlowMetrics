from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.health import router as health_router
from app.routes.runs import router as runs_router
from app.routes.samples import router as samples_router

app = FastAPI(title="FlowMetrics API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(runs_router)
app.include_router(samples_router)