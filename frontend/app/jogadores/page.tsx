"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, Crown } from "lucide-react";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { corTime, iniciais } from "@/lib/times-visual";
import { JogadorModal } from "@/components/jogador-modal";
import { VhSpinner } from "@/components/vh-spinner";
import { API_URL } from "@/lib/api";

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

interface Time {
  id: number;
  nome: string;
}

interface Categoria {
  chave: string;
  label: string;
}

const GRUPOS_CATEGORIAS: { titulo: string; itens: Categoria[] }[] = [
  {
    titulo: "Ataque",
    itens: [
      { chave: "gols", label: "Gols" },
      { chave: "assistencias", label: "Assistências" },
      { chave: "chutes", label: "Chutes" },
      { chave: "chutes_gol", label: "Chutes ao Gol" },
    ],
  },
  {
    titulo: "Defesa",
    itens: [
      { chave: "desarmes", label: "Desarmes" },
      { chave: "faltas_cometidas", label: "Faltas Cometidas" },
      { chave: "faltas_sofridas", label: "Faltas Sofridas" },
      { chave: "defesas", label: "Defesas (goleiros)" },
    ],
  },
  {
    titulo: "Disciplina",
    itens: [
      { chave: "cartoes_amarelos", label: "Cartões Amarelos" },
      { chave: "cartoes_vermelhos", label: "Cartões Vermelhos" },
    ],
  },
];

// A Highlightly (fonte dos dados) so fornece gols/assistencias/cartoes
// por jogador -- chutes, chutes ao gol, desarmes, faltas e defesas so
// existem por time. Essas categorias nunca vao preencher com dado real,
// entao merecem um aviso diferente de "ainda nao importado".
const CATEGORIAS_SEM_DADO_POR_JOGADOR = new Set([
  "chutes",
  "chutes_gol",
  "desarmes",
  "faltas_cometidas",
  "faltas_sofridas",
  "defesas",
]);

const TODAS_CATEGORIAS = GRUPOS_CATEGORIAS.flatMap((g) => g.itens);

function BadgePosicao({ index }: { index: number }) {
  if (index === 0) {
    return (
      <span className="flex w-5 shrink-0 items-center justify-center">
        <Crown className="size-4 text-primary" strokeWidth={2.5} />
      </span>
    );
  }
  const cor =
    index === 1 ? "text-slate-300" : index === 2 ? "text-amber-600" : "text-muted-foreground";
  return (
    <span className={`flex w-5 shrink-0 items-center justify-center font-mono text-xs font-semibold ${cor}`}>
      {index + 1}
    </span>
  );
}

export default function Jogadores() {
  const [statSelecionado, setStatSelecionado] = useState("gols");
  const [mando, setMando] = useState("todos");
  const [timeSelecionado, setTimeSelecionado] = useState("");
  const [times, setTimes] = useState<Time[]>([]);
  const [ranking, setRanking] = useState<RankingItem[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [jogadorAbertoId, setJogadorAbertoId] = useState<number | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/times/`)
      .then((r) => r.json())
      .then((dados: Time[]) => setTimes(dados))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setCarregando(true);
    setErro(null);

    const mandoParam = mando === "todos" ? "" : `&mando=${mando}`;
    const timeParam = timeSelecionado ? `&time_id=${timeSelecionado}` : "";

    fetch(`${API_URL}/jogadores/ranking/${statSelecionado}?limit=20${mandoParam}${timeParam}`)
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
  }, [statSelecionado, mando, timeSelecionado]);

  const categoriaAtual = TODAS_CATEGORIAS.find((c) => c.chave === statSelecionado) ?? TODAS_CATEGORIAS[0];

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
          <nav className="flex gap-4 overflow-x-auto pb-1 lg:flex-col lg:overflow-visible lg:pb-0">
            {GRUPOS_CATEGORIAS.map((grupo) => (
              <div key={grupo.titulo} className="flex shrink-0 gap-1.5 lg:flex-col lg:gap-1">
                <span className="hidden px-3 text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground/70 lg:block">
                  {grupo.titulo}
                </span>
                {grupo.itens.map((cat) => {
                  const semDado = CATEGORIAS_SEM_DADO_POR_JOGADOR.has(cat.chave);
                  return (
                    <button
                      key={cat.chave}
                      type="button"
                      onClick={() => setStatSelecionado(cat.chave)}
                      className={`shrink-0 rounded-md px-3 py-2 text-left text-sm font-medium whitespace-nowrap transition-colors ${
                        statSelecionado === cat.chave
                          ? "bg-primary/10 text-primary"
                          : semDado
                            ? "text-muted-foreground/50 hover:bg-muted hover:text-muted-foreground"
                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                      }`}
                    >
                      {cat.label}
                      {semDado && <span className="ml-1 text-[10px]">· sem dado</span>}
                    </button>
                  );
                })}
              </div>
            ))}
          </nav>

          <section>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                {categoriaAtual.label}
              </h2>
              <div className="flex flex-wrap items-center gap-2">
                <select
                  value={timeSelecionado}
                  onChange={(e) => setTimeSelecionado(e.target.value)}
                  className="rounded-lg border border-input bg-card px-3 py-1.5 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                  <option value="">Top 20 da liga</option>
                  {times.map((time) => (
                    <option key={time.id} value={time.id}>
                      {time.nome}
                    </option>
                  ))}
                </select>
                <ToggleGroup
                  variant="outline"
                  size="sm"
                  value={[mando]}
                  onValueChange={(v: string[]) => v[0] && setMando(v[0])}
                >
                  <ToggleGroupItem value="todos">Todos</ToggleGroupItem>
                  <ToggleGroupItem value="casa">Casa</ToggleGroupItem>
                  <ToggleGroupItem value="fora">Fora</ToggleGroupItem>
                </ToggleGroup>
              </div>
            </div>

            {!carregando && ranking.length > 0 && (
              <p className="mt-1 text-xs text-muted-foreground">
                {timeSelecionado
                  ? `Elenco completo de ${times.find((t) => String(t.id) === timeSelecionado)?.nome ?? "time"} — toque em um jogador para ver os detalhes.`
                  : "Toque em um jogador para ver os detalhes."}
              </p>
            )}

            {carregando && (
              <div className="mt-3 flex min-h-64 items-center justify-center">
                <VhSpinner />
              </div>
            )}

            {erro && <p className="mt-3 text-destructive">Erro: {erro}</p>}

            {!carregando && !erro && ranking.length === 0 && (
              <div className="mt-3 rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
                {CATEGORIAS_SEM_DADO_POR_JOGADOR.has(statSelecionado) ? (
                  <>
                    A fonte de dados não fornece {categoriaAtual.label.toLowerCase()} por jogador, apenas por
                    time — essa categoria não deve preencher.
                  </>
                ) : (
                  "Ainda não há dados suficientes de jogadores importados para essa categoria. Em breve."
                )}
              </div>
            )}

            {!carregando && ranking.length > 0 && (
              <div className="mt-3 flex items-center justify-end gap-6 px-3 text-[10px] uppercase tracking-wide text-muted-foreground/70">
                <span>Total na temporada / média por jogo</span>
              </div>
            )}

            {!carregando && ranking.length > 0 && (
              <ul className="mt-1.5 grid gap-1.5">
                {ranking.map((item, index) => {
                  const cores = corTime(item.time_nome ?? "");
                  return (
                    <li key={item.jogador_id}>
                      <button
                        type="button"
                        onClick={() => setJogadorAbertoId(item.jogador_id)}
                        className="flex w-full items-center gap-3 rounded-md bg-card px-3 py-2.5 text-left ring-1 ring-foreground/10 transition-colors hover:ring-primary/40"
                      >
                        <BadgePosicao index={index} />
                        <span
                          className={`flex size-8 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold ${
                            cores.textoEscuro ? "text-black" : "text-white"
                          }`}
                          style={{ backgroundColor: cores.fundo, borderColor: cores.borda }}
                        >
                          {iniciais(item.nome)}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium">{item.nome}</p>
                          <p className="truncate text-[11px] text-muted-foreground">
                            {item.posicao ?? "—"} · {item.time_nome ?? "Sem clube"} · {item.jogos} jogos
                          </p>
                        </div>
                        <div className="shrink-0 text-right">
                          <p className="font-mono text-lg font-bold tabular-nums text-primary">{item.total}</p>
                          <p className="text-[10px] text-muted-foreground">
                            <span className="font-mono tabular-nums">{item.media.toFixed(2)}</span> por jogo
                          </p>
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
