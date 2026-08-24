"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, Sparkles, Eye } from "lucide-react";
import { VhSpinner } from "@/components/vh-spinner";
import { ListaDestaques, SequenciaBadges, type Destaque } from "@/components/lista-destaques";
import { BilheteSimplesCard, BilheteMultiplaCard, type Perna } from "@/components/bilhete-card";
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
  resumo: string | null;
  destaques_mandante: Destaque[];
  destaques_visitante: Destaque[];
  destaques_jogadores_mandante: DestaqueJogador[];
  destaques_jogadores_visitante: DestaqueJogador[];
  bilhete_simples: BilheteSimples | null;
  bilhete_multipla: BilheteMultipla | null;
}

function fraseJogador(nomeTime: string, j: DestaqueJogador) {
  const melhor = j.destaques[0];
  const porcentagem = Math.round(melhor.taxa * 100);
  const acao =
    melhor.tipo === "booleano" ? melhor.label.toLowerCase() : `mais de ${melhor.linha} ${melhor.label.toLowerCase()}`;

  return (
    <>
      <span className="font-semibold">{j.nome}</span>
      {j.posicao && <span className="text-muted-foreground"> ({j.posicao})</span>} · {nomeTime} — {acao} em{" "}
      <span className="font-mono font-semibold">{porcentagem}%</span> dos últimos {melhor.total} jogos
    </>
  );
}

export default function AnalisePartida() {
  const params = useParams();
  const partidaId = params.partidaId as string;

  const [partida, setPartida] = useState<PartidaResumo | null>(null);
  const [analise, setAnalise] = useState<AnaliseResponse | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

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
                {analise?.bilhete_simples && (
                  <BilheteSimplesCard
                    perna={analise.bilhete_simples.perna}
                    confianca={analise.bilhete_simples.confianca}
                  />
                )}
                {analise?.bilhete_multipla && (
                  <BilheteMultiplaCard
                    pernas={analise.bilhete_multipla.pernas}
                    confiancaCombinada={analise.bilhete_multipla.confianca_combinada}
                  />
                )}
              </div>
            )}

            {analise?.disponivel && analise.resumo && (
              <div className="mt-3 flex items-start justify-center gap-1.5 text-center">
                <p className="text-xs italic leading-relaxed text-muted-foreground">“{analise.resumo}”</p>
                <span className="mt-0.5 shrink-0 rounded-full bg-violet-500/15 px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-wide text-violet-400">
                  PRO
                </span>
              </div>
            )}

            {!analise?.bilhete_simples && (
              <div className="mt-6 rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
                {partida.status === "finalizada"
                  ? "A análise da IA é gerada apenas para partidas que ainda vão acontecer."
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
                  <span className="ml-auto shrink-0 rounded-full bg-violet-500/15 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wide text-violet-400">
                    PRO
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

            {analise && (analise.destaques_mandante.length > 0 || analise.destaques_visitante.length > 0) && (
              <div className="mt-4 grid gap-4 rounded-lg border border-border bg-card/60 p-4 sm:grid-cols-2 sm:divide-x sm:divide-border">
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
          </>
        )}
      </div>
    </main>
  );
}
