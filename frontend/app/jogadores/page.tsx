"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { corTime, iniciais } from "@/lib/times-visual";
import { JogadorModal } from "@/components/jogador-modal";

interface RankingItem {
  jogador_id: number;
  nome: string;
  posicao: string | null;
  time_id: number | null;
  time_nome: string | null;
  jogos: number;
  total: number;
  media: number;
}

interface RankingResponse {
  stat: string;
  ranking: RankingItem[];
}

const CATEGORIAS: { chave: string; label: string }[] = [
  { chave: "gols", label: "Gols" },
  { chave: "assistencias", label: "Assistências" },
  { chave: "chutes", label: "Chutes" },
  { chave: "chutes_gol", label: "Chutes ao Gol" },
  { chave: "desarmes", label: "Desarmes" },
  { chave: "faltas_cometidas", label: "Faltas Cometidas" },
  { chave: "faltas_sofridas", label: "Faltas Sofridas" },
  { chave: "cartoes_amarelos", label: "Cartões Amarelos" },
  { chave: "cartoes_vermelhos", label: "Cartões Vermelhos" },
];

export default function Jogadores() {
  const [statSelecionado, setStatSelecionado] = useState("gols");
  const [ranking, setRanking] = useState<RankingItem[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [jogadorAbertoId, setJogadorAbertoId] = useState<number | null>(null);

  useEffect(() => {
    setCarregando(true);
    setErro(null);

    fetch(`http://127.0.0.1:8000/jogadores/ranking/${statSelecionado}?limit=20`)
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar ranking");
        return r.json();
      })
      .then((dados: RankingResponse) => {
        setRanking(dados.ranking);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, [statSelecionado]);

  const categoriaAtual = CATEGORIAS.find((c) => c.chave === statSelecionado) ?? CATEGORIAS[0];

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-5xl">
        <Link
          href="/brasileirao"
          className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Brasileirão
        </Link>

        <h1 className="mt-2 font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
          Jogadores
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Ranking de estatísticas individuais do Brasileirão Série A.
        </p>

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[190px_1fr] lg:items-start">
          <nav className="flex gap-1.5 overflow-x-auto pb-1 lg:flex-col lg:overflow-visible lg:pb-0">
            {CATEGORIAS.map((cat) => (
              <button
                key={cat.chave}
                type="button"
                onClick={() => setStatSelecionado(cat.chave)}
                className={`shrink-0 rounded-md px-3 py-2 text-left text-sm font-medium whitespace-nowrap transition-colors ${
                  statSelecionado === cat.chave
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </nav>

          <section>
            <div className="flex items-center justify-between">
              <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                {categoriaAtual.label}
              </h2>
              {!carregando && ranking.length > 0 && (
                <p className="text-xs text-muted-foreground">Toque em um jogador para ver os detalhes.</p>
              )}
            </div>

            {carregando && (
              <div className="mt-3 grid gap-1.5">
                {Array.from({ length: 8 }).map((_, i) => (
                  <Skeleton key={i} className="h-14 w-full rounded-md" />
                ))}
              </div>
            )}

            {erro && <p className="mt-3 text-destructive">Erro: {erro}</p>}

            {!carregando && !erro && ranking.length === 0 && (
              <div className="mt-3 rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
                Ainda não há dados individuais de jogadores importados. Em breve.
              </div>
            )}

            {!carregando && ranking.length > 0 && (
              <ul className="mt-3 grid gap-1.5">
                {ranking.map((item, index) => {
                  const cores = corTime(item.time_nome ?? "");
                  return (
                    <li key={item.jogador_id}>
                      <button
                        type="button"
                        onClick={() => setJogadorAbertoId(item.jogador_id)}
                        className="flex w-full items-center gap-3 rounded-md bg-card px-3 py-2.5 text-left ring-1 ring-foreground/10 transition-colors hover:ring-primary/40"
                      >
                        <span className="w-5 shrink-0 text-center font-mono text-xs text-muted-foreground">
                          {index + 1}
                        </span>
                        <span
                          className={`flex size-8 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold ${
                            cores.textoEscuro ? "text-black" : "text-white"
                          }`}
                          style={{ backgroundColor: cores.fundo, borderColor: cores.borda }}
                        >
                          {iniciais(item.time_nome ?? item.nome)}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium">{item.nome}</p>
                          <p className="truncate text-[11px] text-muted-foreground">
                            {item.posicao ?? "—"} · {item.time_nome ?? "Sem clube"} · {item.jogos} jogos
                          </p>
                        </div>
                        <div className="shrink-0 text-right">
                          <p className="font-mono text-lg font-bold tabular-nums text-primary">{item.total}</p>
                          <p className="text-[10px] text-muted-foreground">média {item.media}</p>
                        </div>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        </div>
      </div>

      <JogadorModal jogadorId={jogadorAbertoId} onClose={() => setJogadorAbertoId(null)} />
    </main>
  );
}
