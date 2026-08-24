# 📈 Roadmap — VEAGA

Este documento acompanha a evolução real do projeto, desde a primeira versão local até a plataforma pública no ar hoje.

---

## 🟢 Fase 1 — Fundação

- [x] Criar repositório no GitHub
- [x] Definir objetivo do projeto
- [x] Criar documentação inicial
- [x] Configurar ambiente de desenvolvimento
- [x] Criar estrutura do projeto
- [x] Configurar Git local

---

## 🟢 Fase 2 — Análise de Times

- [x] Criar estrutura de dados dos times
- [x] Adicionar histórico de partidas
- [x] Mostrar últimos jogos
- [x] Identificar vitórias, empates e derrotas
- [x] Calcular gols marcados
- [x] Calcular gols sofridos
- [x] Calcular médias de gols
- [x] Analisar desempenho em casa e fora
- [x] Criar indicadores de tendência

---

## 🟢 Fase 3 — Backend

- [x] Criar API com FastAPI
- [x] Criar endpoints de times
- [x] Criar endpoints de partidas
- [x] Criar endpoints de estatísticas
- [x] Implementar validações
- [ ] Criar testes automatizados (começou em `backend/tests/` com pytest, cobrindo a lógica de linha/taxa de acerto da Dicas da Rodada; resto do backend segue com validação manual + scripts ad-hoc em `backend/scripts/test_*.py`)

---

## 🟢 Fase 4 — Frontend

- [x] Criar interface inicial
- [x] Criar página de times
- [x] Criar página de partidas (rodadas)
- [x] Criar cards de estatísticas
- [x] Criar histórico visual dos jogos
- [x] Criar comparação entre times
- [x] Melhorar experiência do usuário (identidade visual "Súmula", feedback de carregamento em todo o site)

---

## 🟢 Fase 5 — Análise Estatística

- [x] Criar cálculo de probabilidades (vitória/empate/derrota)
- [x] Criar indicadores de confiança (taxas de acerto, suavização de Laplace pra amostra pequena)
- [x] Criar análise de tendências (Dicas da Rodada — sequências por linha fixa, taxa de acerto ≥70%)
- [x] Implementar modelos estatísticos (distribuição de Poisson pro placar mais provável)
- [x] Criar sistema de backtesting (validação retroativa do modelo de projeções, ver Issue #27)

---

## 🔵 Fase 6 — Inteligência Artificial

- [ ] Integrar API de IA (endpoint e cache prontos, falta configurar `GEMINI_API_KEY`)
- [x] Criar análise automática das partidas (prévia por partida agendada, link dedicado no modal — ver Issue de Análise da IA)
- [ ] Gerar explicações baseadas nos dados
- [ ] Criar insights automáticos
- [ ] Avaliar qualidade das respostas

> Estrutura pronta (`/partidas/{id}/analise`, cache em banco pra não gastar chamada de API repetida), usando o free tier do Gemini (Google AI Studio, sem cartão de crédito) — volume real (uma chamada por partida, pra sempre, nunca repete) fica bem abaixo do limite gratuito. Falta só configurar `GEMINI_API_KEY` em produção; até lá degrada pra "em breve". Pensado desde já pra virar recurso premium quando o site tiver assinatura. O desenvolvimento do VEAGA em si já é assistido por IA (Claude Code) do planejamento à implementação — essa fase é sobre IA como parte da experiência pro usuário final, não como ferramenta de desenvolvimento.

---

## 🟣 Fase 7 — Cloud

- [x] Fazer deploy do backend (Render)
- [x] Fazer deploy do frontend (Vercel)
- [x] Configurar banco de dados de produção (Supabase Postgres)
- [ ] Containerizar aplicação com Docker (não foi necessário até agora — Render builda direto do `requirements.txt`)
- [ ] Configurar domínio próprio (hoje usa o subdomínio da Vercel)
- [ ] Configurar CI/CD (deploy hoje é automático a cada push pro `main`, mas sem pipeline de testes antes)
- [ ] Implementar monitoramento

---

## 🔴 Fase 8 — Expansão

- [x] Adicionar análise de jogadores (gols/assistências/cartões reais, Dicas da Rodada estendida pro nível de jogador, backfill histórico completo — todas as 225 partidas já finalizadas)
- [ ] Adicionar mais campeonatos
- [ ] Criar dashboard completo
- [ ] Criar sistema de usuários
- [ ] Criar favoritos
- [ ] Criar alertas
- [ ] Avaliar possibilidades de monetização

---

## 🎯 Objetivo final

Transformar o projeto em uma plataforma pública de análise estatística de futebol, utilizando dados, desenvolvimento de software, Cloud e Inteligência Artificial.

O projeto também é usado como portfólio profissional, demonstrando conhecimentos práticos em desenvolvimento de software e tecnologias modernas — com uma plataforma real no ar, não só um protótipo local.
