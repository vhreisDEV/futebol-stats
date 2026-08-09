from fastapi import FastAPI
from app.routers import times

app = FastAPI(title="Football Analytics Platform")

app.include_router(times.router)

@app.get("/")
def root():
    return {"status": "API rodando"}