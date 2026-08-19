# 🏗️ Arquitetura — VEAGA

Este documento descreve a arquitetura real do projeto em produção.

---

## 🎯 Visão geral

O VEAGA é dividido em três partes com deploy independente:

- **Frontend** — Next.js, hospedado na Vercel
- **Backend / API** — FastAPI, hospedado no Render
- **Banco de dados** — PostgreSQL, hospedado no Supabase

Em desenvolvimento local, o backend usa SQLite por padrão (sem precisar de nenhuma configuração extra) e só passa a usar o Postgres de produção se a variável de ambiente `DATABASE_URL` estiver definida — os dois ambientes rodam com o mesmo código, sem branch nem flag.

---

## 🔄 Fluxo de dados

```text
Highlightly (fonte de dados real do Brasileirão)
       ↓  (scripts de import, backend/scripts/*.py)
Banco de dados (SQLite local / PostgreSQL em produção)
       ↓
Backend FastAPI (Render)
       ↓  (REST, JSON)
Frontend Next.js (Vercel)
       ↓
Usuário
```

Os scripts de import (`importar_partidas.py`, `importar_jogadores.py`) rodam sob demanda, não em pipeline agendado — a cota gratuita da Highlightly (100 requisições/dia) é o principal fator limitante, então os imports são feitos manualmente e de forma incremental (nunca reimportam o que já existe).

---

## 🌐 Deploy

| Camada | Serviço | Observações |
|---|---|---|
| Frontend | Vercel | Deploy automático a cada push no `main`. Domínio: `veaga-psi.vercel.app`. |
| Backend | Render (plano gratuito) | Deploy automático via blueprint (`render.yaml`). "Dorme" após ~15 min sem uso — primeira requisição depois disso demora alguns segundos. |
| Banco de dados | Supabase (plano gratuito) | Escolhido no lugar do Postgres do próprio Render porque o deste último **expira em 30 dias** no plano grátis; o do Supabase não tem prazo, só pausa após 7 dias de inatividade total (reativa com um clique, sem perda de dado). |

### Variáveis de ambiente (produção)

- `DATABASE_URL` — connection string do Supabase (modo "Session pooler")
- `HIGHLIGHTLY_API_KEY` — chave da API de dados
- `FRONTEND_URL` — domínio da Vercel (CORS também libera `*.vercel.app` por padrão via regex, cobrindo previews de branch)
- `NEXT_PUBLIC_API_URL` (frontend, na Vercel) — URL do backend no Render

### CORS

A API não tem nenhuma rota de escrita (só leitura), então o CORS libera por regex qualquer subdomínio de `*.vercel.app` e `*.trycloudflare.com` (usado em testes com túnel), além do `FRONTEND_URL` explícito — risco baixo dado que não há dado sensível nem ação que modifique estado.

---

## 🗄️ Modelo de dados (resumo)

- `Time` — 20 times do Brasileirão, com `id_externo` mapeando pro ID real na Highlightly.
- `Partida` — uma linha por confronto da temporada (380 no total), com `status` (`agendada` / `adiada` / `finalizada`) e todos os campos de estatística nullable — ausência de dado nunca é tratada como zero.
- `Jogador` / `EstatisticaJogadorPartida` — estatística real por jogador (gols, assistências, cartões), limitada ao que a Highlightly disponibiliza nessa granularidade — chutes, desarmes e faltas só existem por time, então ficam `null` por jogador.

---

## 🧪 Ambiente de desenvolvimento

Dois computadores (`home` e `work`), sincronizados via `git pull`/`git push`. Banco local é um arquivo SQLite (`backend/futebol_stats.db`, fora do controle de versão) — seguro apagar e recriar quando o schema muda.
