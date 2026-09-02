"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { JogadorModal } from "@/components/jogador-modal";
import { VhSpinner } from "@/components/vh-spinner";
import { corTime, iniciais } from "@/lib/times-visual";
import { API_URL } from "@/lib/api";

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

const TODAS_CATEGORIAS = GRUPOS_CATEGORIAS.flatMap((g) => g.itens);

interface JogoGrade {
  partida_id: number;
  data: string;
  adversario: string;
  casa_ou_fora: string;
  placar: string | null;
}

interface JogadorGrade {
  jogador_id: number;
  nome: string;
  posicao: string | null;
  total: number;
  media: number;
  valores: (number | null)[];
}

interface GradeResponse {
  stat: string;
  jogos: JogoGrade[];
  jogadores: JogadorGrade[];
}

interface ProximoJogo {
  adversario: string;
  data: string | null;
  casa_ou_fora: string;
}

function formatarData(dataStr: string) {
  const partes = dataStr.split("-");
  if (partes.length === 3) {
    const [ano, mes, dia] = partes;
    return `${dia}/${mes}`;
  }
  return dataStr;
}

export default function GradeJogadoresTime() {
  const params = useParams();
  const timeId = params.id;

  const [nomeTime, setNomeTime] = useState("");
  const [statSelecionado, setStatSelecionado] = useState("desarmes");
  const [quantidade, setQuantidade] = useState(10);
  const [mando, setMando] = useState("todos");
  const [grade, setGrade] = useState<GradeResponse | null>(null);
  const [proximoJogo, setProximoJogo] = useState<ProximoJogo | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [jogadorAbertoId, setJogadorAbertoId] = useState<number | null>(null);

  const categoriaAtual = TODAS_CATEGORIAS.find((c) => c.chave === statSelecionado) ?? TODAS_CATEGORIAS[0];

  useEffect(() => {
    if (!timeId) return;

    setCarregando(true);
    setErro(null);

    const mandoParam = mando === "todos" ? "" : `&mando=${mando}`;

    Promise.all([
      fetch(`${API_URL}/times/${timeId}`).then((r) => {
        if (!r.ok) throw new Error("Time não encontrado");
        return r.json();
      }),
      fetch(
        `${API_URL}/times/${timeId}/grade-jogadores?stat=${statSelecionado}&quantidade=${quantidade}${mandoParam}`
      ).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar a grade de jogadores");
        return r.json();
      }),
    ])
      .then(([dadosTime, dadosGrade]) => {
        setNomeTime(dadosTime.nome);
        setGrade(dadosGrade);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, [timeId, statSelecionado, quantidade, mando]);

  useEffect(() => {
    if (!timeId) return;

    fetch(`${API_URL}/partidas/proxima?time_id=${timeId}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((dados) => {
        if (!dados) {
          setProximoJogo(null);
          return;
        }
        return fetch(`${API_URL}/partidas/${dados.id}`).then((r) => r.json());
      })
      .then((partida) => {
        if (!partida) return;
        const jogaEmCasa = partida.time_mandante_id === Number(timeId);
        setProximoJogo({
          adversario: jogaEmCasa ? partida.time_visitante : partida.time_mandante,
          data: partida.data,
          casa_ou_fora: jogaEmCasa ? "casa" : "fora",
        });
      })
      .catch(() => setProximoJogo(null));
  }, [timeId]);

  const cores = corTime(nomeTime);
  const larguraLabel = 170;
  const larguraTotal = 70;
  const larguraJogo = 84;
  const larguraFixa = larguraLabel + larguraTotal;
  const larguraGrade = grade ? larguraFixa + grade.jogos.length * larguraJogo : larguraFixa;

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between gap-3">
          <Link
            href={`/times/${timeId}`}
            className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
            {nomeTime || "Time"}
          </Link>

          {proximoJogo && (
            <div className="rounded-md border border-border bg-card px-3 py-1.5 text-right text-xs">
              <span className="text-muted-foreground">Próximo jogo</span>{" "}
              <span className="font-semibold text-foreground">
                {proximoJogo.casa_ou_fora === "casa" ? "vs" : "@"} {proximoJogo.adversario}
              </span>
              {proximoJogo.data && (
                <span className="ml-1 text-muted-foreground">({formatarData(proximoJogo.data)})</span>
              )}
            </div>
          )}
        </div>

        <div className="mt-3 flex items-center gap-2">
          {nomeTime && (
            <span
              className={`flex size-9 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold ${cores.textoEscuro ? "text-black" : "text-white"}`}
              style={{ backgroundColor: cores.fundo, borderColor: cores.borda }}
            >
              {iniciais(nomeTime)}
            </span>
          )}
          <h1 className="font-heading text-xl font-semibold uppercase tracking-wide sm:text-2xl">
            {nomeTime} — Estatísticas por Jogador
          </h1>
        </div>

        {erro && <p className="mt-4 text-destructive">Erro: {erro}</p>}

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[190px_1fr] lg:items-start">
          <nav className="flex gap-4 overflow-x-auto pb-1 lg:flex-col lg:overflow-visible lg:pb-0">
            {GRUPOS_CATEGORIAS.map((grupo) => (
              <div key={grupo.titulo} className="flex shrink-0 gap-1.5 lg:flex-col lg:gap-1">
                <span className="hidden px-3 text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground/70 lg:block">
                  {grupo.titulo}
                </span>
                {grupo.itens.map((cat) => (
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
              </div>
            ))}
          </nav>

          <section>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                {categoriaAtual.label}
              </h2>
              <div className="flex flex-wrap items-center gap-2">
                <ToggleGroup
                  variant="outline"
                  size="sm"
                  value={[String(quantidade)]}
                  onValueChange={(v: string[]) => v[0] && setQuantidade(Number(v[0]))}
                >
                  <ToggleGroupItem value="5">Últimos 5</ToggleGroupItem>
                  <ToggleGroupItem value="10">Últimos 10</ToggleGroupItem>
                  <ToggleGroupItem value="20">Últimos 20</ToggleGroupItem>
                  <ToggleGroupItem value="30">Últimos 30</ToggleGroupItem>
                </ToggleGroup>
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

            {!carregando && grade && grade.jogadores.length > 0 && (
              <p className="mt-1 text-xs text-muted-foreground">Toque em um jogador para ver os detalhes.</p>
            )}

            {carregando && (
              <div className="mt-3 flex min-h-64 items-center justify-center">
                <VhSpinner />
              </div>
            )}

            {!carregando && grade && grade.jogadores.length === 0 && (
              <div className="mt-3 rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
                Ainda não há dados suficientes pra essa categoria nesse período.
              </div>
            )}

            {!carregando && grade && grade.jogos.length > 0 && grade.jogadores.length > 0 && (
              <div className="mt-3 overflow-x-auto">
                <div style={{ minWidth: larguraGrade }}>
                  <div
                    className="flex items-center gap-2 pb-1.5 text-[10px] font-medium uppercase tracking-wide text-muted-foreground"
                    style={{ paddingLeft: larguraFixa }}
                  >
                    <span>Último jogo</span>
                    <div className="h-px flex-1 bg-border" />
                    <span>Mais antigo</span>
                  </div>

                  <div className="overflow-hidden rounded-lg ring-1 ring-border">
                    <div
                      className="grid gap-[2px] bg-border/70 text-xs"
                      style={{
                        gridTemplateColumns: `${larguraLabel}px ${larguraTotal}px repeat(${grade.jogos.length}, ${larguraJogo}px)`,
                      }}
                    >
                      <div className="bg-card px-2 py-2" />
                      <div className="bg-card px-2 py-2 text-center text-[10px] font-semibold text-muted-foreground">
                        Total
                      </div>
                      {grade.jogos.map((jogo) => (
                        <div key={jogo.partida_id} className="bg-card px-2 py-2 text-center">
                          <p className="text-[11px] text-muted-foreground">{formatarData(jogo.data)}</p>
                          <p className="mt-0.5 truncate font-medium text-foreground">{jogo.adversario}</p>
                          <p className="mt-0.5 text-[10px] text-muted-foreground">
                            {jogo.casa_ou_fora === "casa" ? "Casa" : "Fora"}
                          </p>
                        </div>
                      ))}

                      {grade.jogadores.map((jogador) => (
                        <button
                          key={jogador.jogador_id}
                          type="button"
                          onClick={() => setJogadorAbertoId(jogador.jogador_id)}
                          className="contents"
                        >
                          <div className="bg-background px-2 py-2 text-left text-[11px] text-foreground hover:bg-muted">
                            <p className="truncate font-medium">{jogador.nome}</p>
                            <p className="text-[10px] text-muted-foreground">{jogador.posicao ?? "—"}</p>
                          </div>
                          <div className="bg-background px-2 py-2 text-center font-mono font-semibold tabular-nums text-primary hover:bg-muted">
                            {jogador.total}
                          </div>
                          {jogador.valores.map((valor, index) => (
                            <div
                              key={index}
                              className="bg-background px-2 py-2 text-center font-mono tabular-nums text-foreground hover:bg-muted"
                            >
                              {valor === null ? "" : valor}
                            </div>
                          ))}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>

      <JogadorModal jogadorId={jogadorAbertoId} onClose={() => setJogadorAbertoId(null)} />
    </main>
  );
}
