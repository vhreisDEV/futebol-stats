import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import times, projecoes, rodadas, classificacao, partidas, jogadores, destaques

app = FastAPI(title="VEAGA")

# FRONTEND_URL: dominio final da Vercel (ou dominio proprio), setado como
# env var em producao. Sem isso, so localhost e os regex abaixo funcionam.
origins = ["http://localhost:3000"]
if frontend_url := os.getenv("FRONTEND_URL"):
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Tuneis rapidos do Cloudflare (*.trycloudflare.com) e previews da
    # Vercel (*.vercel.app, um subdominio novo por branch/PR) usam
    # dominio aleatorio -- API e toda leitura (sem rota de escrita),
    # risco baixo em liberar por regex.
    allow_origin_regex=r"https://.*\.(trycloudflare\.com|vercel\.app)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(times.router)
app.include_router(projecoes.router)
app.include_router(rodadas.router)
app.include_router(classificacao.router)
app.include_router(partidas.router)
app.include_router(jogadores.router)
app.include_router(destaques.router)

@app.get("/")
def root():
    return {"status": "API rodando"}