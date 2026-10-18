from fastapi import FastAPI


app = FastAPI(
    tittle="BetterSelf API",
    version="0.1.0",
    description="API for BetterSelf project"
)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}