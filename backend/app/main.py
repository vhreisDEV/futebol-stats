from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import times, projecoes, rodadas, classificacao, partidas, jogadores

app = FastAPI(title="VEAGA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    # Tuneis rapidos do Cloudflare (cloudflared) usam um subdominio
    # aleatorio *.trycloudflare.com a cada execucao -- liberado so pra
    # teste temporario via link publico, API e toda leitura (sem rota
    # de escrita), risco baixo.
    allow_origin_regex=r"https://.*\.trycloudflare\.com",
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

@app.get("/")
def root():
    return {"status": "API rodando"}