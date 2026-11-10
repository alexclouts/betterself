import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from betterself.core.config import settings
from betterself.routers.auth_router import router as auth_router
from betterself.routers.users_router import router as users_router
from betterself.routers.measurement_router import router as measurements_router
from betterself.routers.goal_router import router as goal_router
from betterself.routers.food_router import router as foods_router
from betterself.routers.recipe_router import router as recipes_router
from betterself.routers.consumption_router import router as consumptions_router
from betterself.routers.onboarding_router import router as onboarding_router


app = FastAPI(
    tittle="BetterSelf API",
    version="0.1.0",
    description="API for BetterSelf project"#
)

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8080,http://127.0.0.1:8080",
).split(",")

print("CORS origins réellement utilisées :", allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(measurements_router)
app.include_router(goal_router)
app.include_router(onboarding_router)

app.include_router(foods_router)
app.include_router(recipes_router)
app.include_router(consumptions_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}