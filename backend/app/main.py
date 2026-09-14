from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import calls, stats

app = FastAPI(title="ClearCall API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calls.router)
app.include_router(stats.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
