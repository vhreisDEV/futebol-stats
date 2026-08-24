"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, ChevronDown, Sparkles, Eye, Target, Lock } from "lucide-react";
import { VhSpinner } from "@/components/vh-spinner";
import { ListaDestaques, SequenciaBadges, type Destaque } from "@/components/lista-destaques";
import { BilheteSimplesCard, BilheteMultiplaCard, fraseTotal, type Perna } from "@/components/bilhete-card";
import { API_URL } from "@/lib/api";
import { formatarDataHora } from "@/lib/formatar-data";

interface PartidaResumo {
  id: number;
  data: string | null;
  hora: string | null;
  status: string;
  rodada: number | null;
  time_mandante_id: number;
  time_mandante: string;
  time_visitante_id: number;
  time_visitante: string;
}

interface BilheteSimples {
  perna: Perna;
  confianca: number;
}

interface BilheteMultipla {
  pernas: Perna[];
  confianca_combinada: number;
}

interface DestaqueJogador {
  jogador_id: number;
  nome: string;
  posicao: string | null;
  destaques: Destaque[];
}

interface AnaliseResponse {
  partida_id: number;
  disponivel: boolean;
  dentro_da_janela: boolean;
  resumo: string | null;
  destaques_mandante: Destaque[];
  destaques_visitante: Destaque[];
  destaques_jogadores_mandante: DestaqueJogador[];
  destaques_jogadores_visitante: DestaqueJogador[];
  destaques_totais: Perna[];
  dicas: string | null;
  bilhete_simples: BilheteSimples | null;
  bilhete_multipla: BilheteMultipla | null;
}

function fraseJogador(nomeTime: string, j: DestaqueJogador) {
  const melhor = j.destaques[0];
  const porcentagem = Math.round(melhor.taxa * 100);

  return (
    <>
      <span className="font-semibold">{j.nome}</span>
      {j.posicao && <span className="text-muted-foreground"> ({j.posicao})</span>} · {nomeTime} — costuma{" "}
      {melhor.tipo === "booleano" ? (
        melhor.label.toLowerCase()
      ) : (
        <>
          passar de <span className="font-mono font-bold text-primary">{melhor.linha}</span>{" "}
          {melhor.label.toLowerCase()}
        </>
      )}{" "}
      em <span className="font-mono font-semibold text-primary">{porcentagem}%</span> dos últimos {melhor.total}{" "}
      jogos
    </>
  );
}

// Realca qualquer numero (inteiro ou decimal) dentro de um texto livre
// gerado pela IA -- deixa as linhas/porcentagens saltando aos olhos em
// vez de se perderem no meio da frase corrida.
function destacarNumeros(texto: string, cor: string = "text-primary") {
  return texto.split(/(\d+[.,]\d+|\d+%?)/g).map((parte, i) =>
    /^\d/.test(parte) ? (
      <span key={i} className={`font-mono font-bold ${cor}`}>
        {parte}
      </span>
    ) : (
      <span key={i}>{parte}</span>
    )
  );
}

export default function AnalisePartida() {
  const params = useParams();
  const partidaId = params.partidaId as string;

  const [partida, setPartida] = useState<PartidaResumo | null>(null);
  const [analise, setAnalise] = useState<AnaliseResponse | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [mercadosAbertos, setMercadosAbertos] = useState(false);

  useEffect(() => {
    setCarregando(true);
    setErro(null);

    Promise.all([
      fetch(`${API_URL}/partidas/${partidaId}`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar dados da partida");
        return r.json();
      }),
      fetch(`${API_URL}/partidas/${partidaId}/analise`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar análise");
        return r.json();
      }),
    ])
      .then(([dadosPartida, dadosAnalise]: [PartidaResumo, AnaliseResponse]) => {
        setPartida(dadosPartida);
        setAnalise(dadosAnalise);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, [partidaId]);

  const jogadoresCombinados =
    partida && analise
      ? [
          ...analise.destaques_jogadores_mandante.map((j) => ({ j, nomeTime: partida.time_mandante })),
          ...analise.destaques_jogadores_visitante.map((j) => ({ j, nomeTime: partida.time_visitante })),
        ]
      : [];

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-2xl">
        <Link
          href="/"
          className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Voltar
        </Link>

        <div className="mt-2 flex items-center gap-2">
          <Sparkles className="size-5 text-violet-400" />
          <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
            Análise da IA
          </h1>
        </div>
        <p className="mt-1 text-center text-xs text-muted-foreground">
          <span className="font-semibold text-foreground">Bilhete simples</span> = melhor palpite isolado ·{" "}
          <span className="font-semibold text-foreground">Múltipla</span> = combinação de palpites ·{" "}
          <span className="font-semibold text-foreground">Dicas da IA</span> = tendências do jogo todo
        </p>

        <div className="mt-3 flex items-center gap-2 rounded-lg border border-violet-500/30 bg-violet-500/10 px-3 py-2">
          <Lock className="size-3.5 shrink-0 text-violet-400" />
          <p className="text-[11px] leading-relaxed text-violet-200">
            <span className="font-bold uppercase tracking-wide">Conteúdo PRO</span> — toda essa análise está
            grátis por enquanto, mas em breve vai ser exclusiva pra assinantes.
          </p>
        </div>

        {carregando && (
          <div className="mt-10 flex min-h-64 items-center justify-center">
            <VhSpinner mensagens={["Montando os bilhetes...", "Estudando o confronto..."]} />
          </div>
        )}

        {erro && <p className="mt-6 text-destructive">Erro: {erro}</p>}

        {!carregando && !erro && partida && (
          <>
            <p className="mt-4 text-center text-xs text-muted-foreground">
              {formatarDataHora(partida.data, partida.hora)}
              {partida.rodada !== null && ` · Rodada ${partida.rodada}`}
            </p>
            <p className="mt-1 text-center font-heading text-lg uppercase tracking-wide">
              {partida.time_mandante} <span className="text-muted-foreground">x</span> {partida.time_visitante}
            </p>

            {(analise?.bilhete_simples || analise?.bilhete_multipla) && (
              <div className="mt-6 grid gap-3">
                {analise?.bilhete_simples && <BilheteSimplesCard perna={analise.bilhete_simples.perna} />}
                {analise?.bilhete_multipla && <BilheteMultiplaCard pernas={analise.bilhete_multipla.pernas} />}
              </div>
            )}

            {analise?.disponivel && analise.resumo && (
              <p className="mt-3 text-center text-xs italic leading-relaxed text-muted-foreground">
                “{destacarNumeros(analise.resumo)}”
              </p>
            )}

            {!analise?.bilhete_simples && (
              <div className="mt-6 rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
                {partida.status === "finalizada"
                  ? "A análise da IA é gerada apenas para partidas que ainda vão acontecer."
                  : analise?.dentro_da_janela === false
                    ? "Essa análise ainda não foi liberada — fica disponível a partir da rodada atual."
                    : "Ainda não há mercados suficientes se destacando pra essa partida."}
              </div>
            )}

            {jogadoresCombinados.length > 0 && (
              <div className="mt-4 rounded-lg border border-violet-500/25 bg-card p-4">
                <div className="flex items-center gap-1.5">
                  <Eye className="size-4 text-violet-400" />
                  <span className="text-[11px] font-bold uppercase tracking-wide text-violet-400">
                    Fique de olho
                  </span>
                </div>
                <ul className="mt-2.5 grid gap-2">
                  {jogadoresCombinados.map(({ j, nomeTime }) => (
                    <li key={j.jogador_id} className="rounded-md bg-muted/40 p-2.5">
                      <p className="text-xs leading-relaxed">{fraseJogador(nomeTime, j)}</p>
                      <div className="mt-1.5">
                        <SequenciaBadges destaque={j.destaques[0]} />
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {analise && analise.destaques_totais.length > 0 && (
              <div className="mt-4 rounded-lg border border-emerald-500/25 bg-card p-4">
                <div className="flex items-center gap-1.5">
                  <Target className="size-4 text-emerald-400" />
                  <span className="text-[11px] font-bold uppercase tracking-wide text-emerald-400">
                    Dicas da IA · Totais do jogo
                  </span>
                </div>
                {analise.dicas && (
                  <p className="mt-2 text-xs italic leading-relaxed text-muted-foreground">
                    {destacarNumeros(analise.dicas, "text-emerald-400")}
                  </p>
                )}
                <ul className="mt-2.5 grid gap-1.5">
                  {analise.destaques_totais.map((p, i) => (
                    <li key={i} className="flex items-center gap-2 rounded-md bg-muted/40 p-2 text-xs">
                      <span className="min-w-0 flex-1">{fraseTotal(p)}</span>
                      <span className="shrink-0 font-mono font-semibold text-emerald-400">
                        {Math.round(p.destaque.taxa * 100)}%
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {analise && (analise.destaques_mandante.length > 0 || analise.destaques_visitante.length > 0) && (
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => setMercadosAbertos((v) => !v)}
                  className="flex w-full items-center justify-center gap-1 text-[11px] font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
                >
                  <ChevronDown className={`size-3.5 transition-transform ${mercadosAbertos ? "rotate-180" : ""}`} />
                  {mercadosAbertos ? "Ocultar todos os mercados" : "Ver todos os mercados"}
                </button>

                {mercadosAbertos && (
                  <div className="mt-2 grid gap-4 rounded-lg border border-border bg-card/60 p-4 sm:grid-cols-2 sm:divide-x sm:divide-border">
                    <div className="min-w-0">
                      <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground/70">
                        {partida.time_mandante} em casa
                      </p>
                      <div className="mt-1.5">
                        <ListaDestaques
                          time={partida.time_mandante}
                          mandoLabel="em casa"
                          destaques={analise.destaques_mandante}
                          mostrarSequencia
                        />
                      </div>
                    </div>
                    <div className="min-w-0 sm:pl-4">
                      <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground/70">
                        {partida.time_visitante} fora
                      </p>
                      <div className="mt-1.5">
                        <ListaDestaques
                          time={partida.time_visitante}
                          mandoLabel="fora de casa"
                          destaques={analise.destaques_visitante}
                          mostrarSequencia
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
