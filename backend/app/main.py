from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import times

app = FastAPI(title="Football Analytics Platform")

app.add_middleware(
CORSMiddleware,
allow_origins=["http://localhost:3000"],
allow_credentials=True,
allow_methods=[""],
allow_headers=[""],
)

app.include_router(times.router)

@app.get("/")
def root():
    return {"status": "API rodando"}