# ⚽ VEAGA — Football Data & Analytics

Plataforma de análise estatística do Brasileirão Série A 2026, com dados reais, projeções estatísticas e tendências pensadas pra quem acompanha o campeonato de perto — de torcedor a apostador.

**🔗 No ar:** [veaga-psi.vercel.app](https://veaga-psi.vercel.app)

> Rodando no plano gratuito do Render — a primeira visita depois de um tempo sem uso pode levar alguns segundos pra "acordar" o backend. Isso é esperado, não é bug.

## 🎯 Objetivo

O VEAGA nasceu como um projeto de estudo e evoluiu pra uma plataforma pública de verdade: analisa o desempenho de times e jogadores do Brasileirão com base em dados históricos e recentes, compara equipes, projeta estatisticamente os próximos confrontos e aponta tendências que se repetem — tudo com dado real, importado da temporada em andamento.

O projeto também segue sendo usado como forma de estudo e evolução profissional: desenvolvimento de software, Python, análise de dados, APIs, banco de dados e desenvolvimento assistido por Inteligência Artificial na prática, do primeiro commit até o deploy em produção.

## 🚀 Funcionalidades

### Classificação e Rodadas

* Tabela de classificação atualizada (considera jogos atrasados)
* Navegação pelas 38 rodadas do campeonato, com jogos adiados sinalizados
* Zonas de classificação (Libertadores, Pré-Libertadores, Sul-Americana, Rebaixamento)

### Times

* Histórico de jogos, forma recente e sequência de resultados
* Vitórias, empates, derrotas, gols marcados e sofridos
* Desempenho como mandante e visitante
* Estatísticas detalhadas por partida (escanteios, chutes, chutes ao gol, cartões)

### Comparação entre Times

* Comparação lado a lado de médias e indicadores
* Histórico recente de cada equipe
* Filtro por período (últimos 5/10/20/30 jogos) e mando de campo

### Previsão de Jogos

* Gols esperados, probabilidade de resultado (vitória/empate/derrota)
* **Placar mais provável** calculado com distribuição de Poisson (não é só arredondar a média) — mostra os 4 placares mais prováveis com a probabilidade de cada um, não uma resposta seca
* Escanteios, cartões e chutes esperados, com linha de referência e tendência (mais/menos)

### Dicas da Rodada

* Pra cada confronto da próxima rodada, sequências recentes de cada time que chamam atenção — ex.: *"Cruzeiro costuma passar de 4.5 escanteios em casa — bateu em 7/10 jogos (70%)"*
* Cobre escanteios, chutes, chutes ao gol, cartões amarelos, gols marcados, ambas equipes marcam e "não perde"
* Testa contra linhas fixas realistas (as mesmas que uma casa de aposta ofereceria), não contra a própria média do time — evita inflar artificialmente a taxa de acerto
* Mesma lógica estendida pra estatística individual de jogador (gols, assistências, cartões) — os destaques com maior taxa de acerto do elenco de cada time aparecem junto com os do time

### Jogadores

* Ranking de estatísticas individuais (gols, assistências, cartões — dado real da Highlightly)
* Ficha por jogador com filtro de período e mando de campo
* Campos sem dado disponível na fonte (chutes, desarmes, faltas por jogador) aparecem em branco, nunca como zero forjado

## 🛠️ Tecnologias

### Backend

* Python + FastAPI
* SQLAlchemy (SQLite em desenvolvimento local, PostgreSQL em produção)
* [Highlightly](https://highlightly.net) como fonte de dados reais do Brasileirão

### Frontend

* Next.js 16 (App Router, Turbopack) + React 19
* Tailwind CSS v4 + shadcn/ui — identidade visual própria ("Súmula": preto de campeonato + dourado de troféu)

### Infraestrutura

* **Vercel** — frontend
* **Render** — backend (FastAPI)
* **Supabase** — banco Postgres de produção

### Ferramentas de Desenvolvimento

* Git + GitHub (planejamento via Issues/Milestones)
* Claude Code — desenvolvimento assistido por IA, do planejamento à implementação e ao deploy

## 📈 Roadmap

### ✅ v0.1.0 — Estrutura Inicial
Repositório, ambiente de desenvolvimento, backend com FastAPI e frontend inicial com Next.js.

### ✅ v0.2.0 — MVP
Análise de times, histórico de jogos, integração frontend/backend com dado real.

### ✅ v0.3.0 — Comparação e Análise
Comparação entre times, médias de desempenho, melhorias de interface.

### ✅ v0.4.0 — Estatísticas Detalhadas de Partida
Escanteios, chutes, cartões por partida — modelo de dados expandido.

### ✅ v0.5.0 — Projeções Estatísticas
Gols esperados, probabilidade de resultado, escanteios/cartões/chutes esperados, com metodologia validada retroativamente contra dado real.

### ✅ v0.6.0 — Navegação por Rodadas
Tela de rodadas, jogos adiados, endpoints de estatística por rodada.

### ✅ v0.7.0 — Deploy Público, Dados Reais e Dicas da Rodada
Site permanentemente no ar (Vercel + Render + Supabase), estatística real de jogador (gols/assistências/cartões), tendências por time (Dicas da Rodada), placar mais provável via Poisson, e uma leva de correções de dado descobertas ao publicar (SQLite vs Postgres, fuso horário, partidas adiadas).

### Próximas versões

* Completar o backfill histórico de estatística de jogador (em andamento — limitado pela cota diária da API)
* Expansão para outros campeonatos
* Integração com Inteligência Artificial (análises/insights gerados automaticamente)
* Melhorias contínuas de experiência da plataforma

## 🧠 Visão do Projeto

```text
Dados reais (Highlightly)
  ↓
Histórico das partidas
  ↓
Estatísticas dos times
  ↓
Comparação entre equipes
  ↓
Projeções e Dicas da Rodada
  ↓
Estatísticas de jogadores
  ↓
Deploy público (Vercel + Render + Supabase)
  ↓
Inteligência Artificial
  ↓
Plataforma completa
```

Cada etapa foi construída em cima do que já existia, evitando funcionalidades isoladas — a projeção pré-jogo usa a mesma base de médias que a comparação de times, as Dicas da Rodada reaproveitam a mesma lógica de janela de jogos, e por aí vai.

## 📚 Objetivo de Aprendizado

O VEAGA segue sendo, antes de tudo, um projeto de estudo — construído de forma gradual, aplicando na prática:

* Python, FastAPI, APIs REST
* React, Next.js, Tailwind CSS
* Modelagem de banco de dados (SQLite → PostgreSQL)
* Análise de dados e estatística aplicada (distribuições, taxas de acerto, metodologia)
* Deploy em Cloud (Vercel, Render, Supabase)
* Desenvolvimento assistido por Inteligência Artificial, do planejamento à execução

O projeto também serve como portfólio: demonstra, com dado real e no ar, arquitetura de software, organização de código, versionamento e construção de um produto completo do zero até o deploy público.

---

🟢 Em produção — [veaga-psi.vercel.app](https://veaga-psi.vercel.app)
