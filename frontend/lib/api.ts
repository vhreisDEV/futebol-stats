// Base URL da API. Em dev local sem configurar nada, aponta pro
// backend rodando em 127.0.0.1:8000 (mesmo padrao de sempre). Pra
// testar via tunel/deploy, define NEXT_PUBLIC_API_URL no ambiente
// (ex.: frontend/.env.local) apontando pra URL publica do backend.
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export const CAMPEONATO_BRASILEIRAO_ID = 1;

// Trava o SeletorCampeonato (Jogadores, Comparar, Previsao, Dicas) num
// dropdown so-leitura ate os outros campeonatos terem dado completo
// (hoje so Brasileirao, PL e La Liga tem historico suficiente; Bundesliga
// ainda nem tem times sincronizados). A navegacao pela Home entre
// campeonatos continua liberada -- isso so trava a TROCA dentro da mesma
// tela. Reativar quando todas as ligas estiverem com backfill completo.
export const TROCA_CAMPEONATO_HABILITADA = false;
