// Base URL da API. Em dev local sem configurar nada, aponta pro
// backend rodando em 127.0.0.1:8000 (mesmo padrao de sempre). Pra
// testar via tunel/deploy, define NEXT_PUBLIC_API_URL no ambiente
// (ex.: frontend/.env.local) apontando pra URL publica do backend.
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export const CAMPEONATO_BRASILEIRAO_ID = 1;

// Previsao de Jogos, Dicas da Rodada e Comparar Times usam media por
// janela de jogos recentes (ultimos 5/10, separados por mandante/
// visitante) -- fazem pouco sentido com menos de ~2 jogos em casa e 2
// fora. Cada liga libera essas 3 telas sozinha assim que sua propria
// rodada_atual bate esse minimo (ver issue #46), em vez de uma trava
// global unica pra todas as ligas de uma vez. Times e Jogadores (o
// ranking da liga, sem janela nenhuma -- so soma da temporada) nunca
// dependeram disso, ficam sempre liberados.
export const RODADA_MINIMA_FUNCOES_AVANCADAS = 5;

// Username do bot do Telegram (sem "@"). Configura via
// NEXT_PUBLIC_TELEGRAM_BOT_USERNAME depois de criar o bot no @BotFather
// -- enquanto vazio, o link de inscrição fica escondido.
export const TELEGRAM_BOT_USERNAME = process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME ?? "";

// URL completa do canal do WhatsApp (formato whatsapp.com/channel/...).
// Enquanto vazio, o link fica escondido -- mesmo padrao do Telegram acima.
export const WHATSAPP_CHANNEL_URL = process.env.NEXT_PUBLIC_WHATSAPP_CHANNEL_URL ?? "";
