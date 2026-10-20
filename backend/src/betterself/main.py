import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from betterself.core.config import settings
from betterself.users.router import router as users_router
from betterself.measurements.router import router as measurements_router

app = FastAPI(
    tittle="BetterSelf API",
    version="0.1.0",
    description="API for BetterSelf project"
)

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(users_router)
app.include_router(measurements_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}