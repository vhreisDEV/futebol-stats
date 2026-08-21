"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ChevronLeft,
  Flame,
  Flag,
  Target,
  Crosshair,
  RectangleVertical,
  CircleDot,
  ArrowLeftRight,
  ShieldCheck,
  Sparkles,
  type LucideIcon,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { VhSpinner } from "@/components/vh-spinner";
import { corTime, iniciais } from "@/lib/times-visual";
import { API_URL } from "@/lib/api";
import { formatarDataHora } from "@/lib/formatar-data";

interface Destaque {
  stat: string;
  label: string;
  tipo: "quantidade" | "booleano";
  linha: number;
  acertos: number;
  total: number;
  taxa: number;
  sequencia: number[];
  media: number;
}

interface DestaqueJogador {
  jogador_id: number;
  nome: string;
  posicao: string | null;
  destaques: Destaque[];
}

interface JogoComDestaques {
  partida_id: number;
  data: string | null;
  hora: string | null;
  rodada: number;
  time_mandante_id: number;
  time_mandante: string;
  time_visitante_id: number;
  time_visitante: string;
  destaques_mandante: Destaque[];
  destaques_visitante: Destaque[];
  destaques_jogadores_mandante: DestaqueJogador[];
  destaques_jogadores_visitante: DestaqueJogador[];
}

interface DestaquesRodadaResponse {
  rodada: number;
  jogos: JogoComDestaques[];
}

interface RodadaAtualResponse {
  rodada_atual: number;
  rodada_maxima: number;
}

const ICONE_STAT: Record<string, { icon: LucideIcon; cor: string }> = {
  gols_marcados: { icon: CircleDot, cor: "text-emerald-400" },
  escanteios_a_favor: { icon: Flag, cor: "text-blue-400" },
  chutes_a_favor: { icon: Target, cor: "text-violet-400" },
  chutes_gol_a_favor: { icon: Crosshair, cor: "text-rose-400" },
  cartoes_amarelos: { icon: RectangleVertical, cor: "text-amber-400" },
  ambas_marcam: { icon: ArrowLeftRight, cor: "text-cyan-400" },
  sem_perder: { icon: ShieldCheck, cor: "text-lime-400" },
  gols: { icon: CircleDot, cor: "text-emerald-400" },
  assistencias: { icon: Sparkles, cor: "text-fuchsia-400" },
};

function BlocoJogadores({ destaquesJogadores }: { destaquesJogadores: DestaqueJogador[] }) {
  if (destaquesJogadores.length === 0) return null;

  return (
    <div className="mt-3 border-t border-border/60 pt-3">
      <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
        Jogadores em destaque
      </p>
      <ul className="mt-2 grid gap-1.5">
        {destaquesJogadores.map((j) => {
          const melhor = j.destaques[0];
          const { icon: Icon, cor } = ICONE_STAT[melhor.stat] ?? { icon: Flag, cor: "text-muted-foreground" };
          const porcentagem = Math.round(melhor.taxa * 100);

          return (
            <li key={j.jogador_id} className="flex items-start gap-2 rounded-md bg-muted/40 p-2">
              <Icon className={`mt-0.5 size-3.5 shrink-0 ${cor}`} />
              <p className="text-xs leading-relaxed text-foreground">
                <span className="font-semibold">{j.nome}</span>
                {j.posicao ? <span className="text-muted-foreground"> ({j.posicao})</span> : null} costuma passar de{" "}
                <span className="font-mono font-semibold text-primary">{melhor.linha}</span>{" "}
                {melhor.label.toLowerCase()} —{" "}
                <span className="font-mono font-semibold">
                  {melhor.acertos}/{melhor.total}
                </span>{" "}
                jogos ({porcentagem}%)
              </p>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function BlocoTime({
  time,
  mandoLabel,
  destaques,
  destaquesJogadores,
}: {
  time: string;
  mandoLabel: "em casa" | "fora de casa";
  destaques: Destaque[];
  destaquesJogadores: DestaqueJogador[];
}) {
  const cores = corTime(time);

  return (
    <div className="min-w-0 flex-1">
      <div className="flex items-center gap-2">
        <span
          className={`flex size-7 shrink-0 items-center justify-center rounded-full border-2 text-[10px] font-bold ${
            cores.textoEscuro ? "text-black" : "text-white"
          }`}
          style={{ backgroundColor: cores.fundo, borderColor: cores.borda }}
        >
          {iniciais(time)}
        </span>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold">{time}</p>
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{mandoLabel}</p>
        </div>
      </div>

      {destaques.length === 0 ? (
        <p className="mt-2.5 text-xs text-muted-foreground/70">Nada que se destaque {mandoLabel}.</p>
      ) : (
        <ul className="mt-2.5 grid gap-2">
          {destaques.map((d) => {
            const { icon: Icon, cor } = ICONE_STAT[d.stat] ?? { icon: Flag, cor: "text-muted-foreground" };
            const porcentagem = Math.round(d.taxa * 100);
            const frase =
              d.stat === "ambas_marcam" ? (
                <>
                  Nos jogos de <span className="font-semibold">{time}</span> {mandoLabel}, ambas equipes costumam
                  marcar —{" "}
                  <span className="font-mono font-semibold">
                    {d.acertos}/{d.total}
                  </span>{" "}
                  jogos ({porcentagem}%)
                </>
              ) : d.stat === "sem_perder" ? (
                <>
                  <span className="font-semibold">{time}</span> costuma não perder {mandoLabel} —{" "}
                  <span className="font-mono font-semibold">
                    {d.acertos}/{d.total}
                  </span>{" "}
                  jogos ({porcentagem}%)
                </>
              ) : (
                <>
                  <span className="font-semibold">{time}</span> costuma passar de{" "}
                  <span className="font-mono font-semibold text-primary">{d.linha}</span> {d.label.toLowerCase()}{" "}
                  {mandoLabel} —{" "}
                  <span className="font-mono font-semibold">
                    {d.acertos}/{d.total}
                  </span>{" "}
                  jogos ({porcentagem}%)
                </>
              );

            return (
              <li key={d.stat} className="rounded-md bg-muted/40 p-2.5">
                <div className="flex items-start gap-2">
                  <Icon className={`mt-0.5 size-3.5 shrink-0 ${cor}`} />
                  <p className="text-xs leading-relaxed text-foreground">{frase}</p>
                </div>
                <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-background/60">
                  <div className={`h-full rounded-full bg-current ${cor}`} style={{ width: `${porcentagem}%` }} />
                </div>
                <p className="mt-1.5 flex flex-wrap gap-1 pl-5.5">
                  {d.sequencia
                    .slice()
                    .reverse()
                    .map((v, i) => (
                      <span
                        key={i}
                        className={`rounded px-1.5 py-0.5 font-mono text-[10px] tabular-nums ${
                          v > d.linha ? "bg-primary/15 font-semibold text-primary" : "bg-background/60 text-muted-foreground/70"
                        }`}
                      >
                        {d.tipo === "booleano" ? (v > d.linha ? "✓" : "✗") : v}
                      </span>
                    ))}
                </p>
              </li>
            );
          })}
        </ul>
      )}

      <BlocoJogadores destaquesJogadores={destaquesJogadores} />
    </div>
  );
}

export default function Dicas() {
  const [rodadaMaxima, setRodadaMaxima] = useState<number | null>(null);
  const [rodadaSelecionada, setRodadaSelecionada] = useState<number | null>(null);
  const [jogos, setJogos] = useState<JogoComDestaques[]>([]);
  const [carregandoInicial, setCarregandoInicial] = useState(true);
  const [carregandoRodada, setCarregandoRodada] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/rodadas/atual`)
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar a rodada atual");
        return r.json();
      })
      .then((dados: RodadaAtualResponse) => {
        setRodadaMaxima(dados.rodada_maxima);
        setRodadaSelecionada(Math.min(dados.rodada_atual + 1, dados.rodada_maxima));
        setCarregandoInicial(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregandoInicial(false);
      });
  }, []);

  useEffect(() => {
    if (rodadaSelecionada === null) return;

    setCarregandoRodada(true);

    fetch(`${API_URL}/destaques/rodada/${rodadaSelecionada}`)
      .then((r) => {
        if (r.status === 404) return { rodada: rodadaSelecionada, jogos: [] };
        if (!r.ok) throw new Error("Erro ao buscar destaques da rodada");
        return r.json();
      })
      .then((dados: DestaquesRodadaResponse) => {
        setJogos(dados.jogos);
        setCarregandoRodada(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregandoRodada(false);
      });
  }, [rodadaSelecionada]);

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-destructive">
        <p>Erro: {erro}</p>
      </main>
    );
  }

  if (carregandoInicial || rodadaSelecionada === null || rodadaMaxima === null) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <VhSpinner />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-3xl">
        <Link
          href="/brasileirao"
          className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Brasileirão
        </Link>

        <div className="mt-2 flex items-center gap-2">
          <Flame className="size-6 text-emerald-400" />
          <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
            Dicas da Rodada
          </h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Sequências recentes de cada time que vêm se repetindo, pros confrontos que ainda vão acontecer.
        </p>

        <div className="mx-auto mt-6 flex w-fit flex-col items-center justify-center rounded-lg border border-border bg-card px-6 py-1.5">
          <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground">
            Próxima rodada
          </span>
          <span className="font-mono text-xl font-bold tabular-nums text-primary sm:text-2xl">
            {rodadaSelecionada}
            <span className="text-xs font-normal text-muted-foreground sm:text-sm"> / {rodadaMaxima}</span>
          </span>
        </div>

        {carregandoRodada ? (
          <div className="mt-8 flex min-h-40 items-center justify-center">
            <VhSpinner />
          </div>
        ) : jogos.length === 0 ? (
          <div className="mt-8 rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
            Nenhuma sequência chamativa encontrada pra essa rodada.
          </div>
        ) : (
          <div className="mt-6 grid gap-3">
            {jogos.map((jogo) => (
              <Card key={jogo.partida_id} className="overflow-hidden border-primary/15">
                <CardContent>
                  <p className="text-center text-xs uppercase tracking-wide text-muted-foreground">
                    {formatarDataHora(jogo.data, jogo.hora)}
                  </p>
                  <p className="mt-1 text-center font-heading text-base font-semibold uppercase tracking-wide">
                    {jogo.time_mandante}
                    <span className="mx-2 text-muted-foreground">x</span>
                    {jogo.time_visitante}
                  </p>
                  <div className="mt-4 grid gap-4 sm:grid-cols-2 sm:divide-x sm:divide-border">
                    <BlocoTime
                      time={jogo.time_mandante}
                      mandoLabel="em casa"
                      destaques={jogo.destaques_mandante}
                      destaquesJogadores={jogo.destaques_jogadores_mandante}
                    />
                    <div className="sm:pl-4">
                      <BlocoTime
                        time={jogo.time_visitante}
                        mandoLabel="fora de casa"
                        destaques={jogo.destaques_visitante}
                        destaquesJogadores={jogo.destaques_jogadores_visitante}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
