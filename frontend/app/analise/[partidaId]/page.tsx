"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, Sparkles } from "lucide-react";
import { VhSpinner } from "@/components/vh-spinner";
import { NotaPartida } from "@/components/nota-partida";
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

interface NotasPartida {
  equilibrio: number | null;
  poder_ofensivo_mandante: number | null;
  poder_ofensivo_visitante: number | null;
  intensidade: number | null;
  confianca: number | null;
}

interface AnaliseResponse {
  partida_id: number;
  disponivel: boolean;
  texto: string | null;
  notas: NotasPartida | null;
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
          <Sparkles className="size-5 text-primary" />
          <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
            Análise da IA
          </h1>
        </div>

        {carregando && (
          <div className="mt-10 flex min-h-64 items-center justify-center">
            <VhSpinner mensagens={["Gerando a análise...", "Estudando o confronto..."]} />
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

            {analise?.notas && (
              <div className="mt-6 grid grid-cols-2 gap-x-6 gap-y-4 rounded-lg border border-border bg-card p-4 sm:grid-cols-5">
                <NotaPartida label="Equilíbrio" nota={analise.notas.equilibrio} />
                <NotaPartida label={`Ataque ${partida.time_mandante}`} nota={analise.notas.poder_ofensivo_mandante} />
                <NotaPartida label={`Ataque ${partida.time_visitante}`} nota={analise.notas.poder_ofensivo_visitante} />
                <NotaPartida label="Intensidade" nota={analise.notas.intensidade} />
                <NotaPartida label="Confiança" nota={analise.notas.confianca} />
              </div>
            )}

            {analise?.disponivel && analise.texto ? (
              <div className="mt-4 rounded-lg border border-violet-500/25 bg-card p-5">
                <span className="mb-3 inline-block rounded-full bg-violet-500/15 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wide text-violet-400">
                  PRO
                </span>
                {analise.texto.split("\n").filter(Boolean).map((paragrafo, i) => (
                  <p key={i} className="text-sm leading-relaxed text-foreground/90 [&:not(:first-child)]:mt-3">
                    {paragrafo}
                  </p>
                ))}
              </div>
            ) : (
              <div className="mt-6 rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
                {partida.status === "finalizada"
                  ? "A análise da IA é gerada apenas para partidas que ainda vão acontecer."
                  : "Essa análise ainda está em preparação — o recurso está em construção e chega em breve."}
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
