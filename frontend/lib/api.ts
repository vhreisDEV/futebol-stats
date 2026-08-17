// Base URL da API. Em dev local sem configurar nada, aponta pro
// backend rodando em 127.0.0.1:8000 (mesmo padrao de sempre). Pra
// testar via tunel/deploy, define NEXT_PUBLIC_API_URL no ambiente
// (ex.: frontend/.env.local) apontando pra URL publica do backend.
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
