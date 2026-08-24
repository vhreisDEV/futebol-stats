// Base URL da API. Em dev local sem configurar nada, aponta pro
// backend rodando em 127.0.0.1:8000 (mesmo padrao de sempre). Pra
// testar via tunel/deploy, define NEXT_PUBLIC_API_URL no ambiente
// (ex.: frontend/.env.local) apontando pra URL publica do backend.
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// Todas as telas hoje sao especificas do Brasileirao (a home/navegacao
// multi-campeonato ainda nao existe) -- fixo por enquanto pra nao misturar
// times/partidas de outras ligas ja importadas (ex.: Premier League) nessas
// paginas. Trocar por um campeonato selecionavel quando essa navegacao existir.
export const CAMPEONATO_BRASILEIRAO_ID = 1;
