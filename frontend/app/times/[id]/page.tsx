"use client";

import { Fragment, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, ChevronRight, TrendingUp, Users, BarChart3 } from "lucide-react";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { PartidaModal } from "@/components/partida-modal";
import { NavChip } from "@/components/nav-chip";
import { VhSpinner } from "@/components/vh-spinner";
import { corTime, iniciais } from "@/lib/times-visual";
import { API_URL, CAMPEONATO_BRASILEIRAO_ID } from "@/lib/api";

interface Jogo {
  id: number;
  data: string | null;
  adversario: string;
  casa_ou_fora: string;
  resultado: string;
  gols_time: number;
  gols_adversario: number;
  escanteios_time: number | null;
  escanteios_adversario: number | null;
  escanteios_1t_time: number | null;
  escanteios_1t_adversario: number | null;
  escanteios_2t_time: number | null;
  escanteios_2t_adversario: number | null;
  chutes_time: number | null;
  chutes_adversario: number | null;
  chutes_1t_time: number | null;
  chutes_1t_adversario: number | null;
  chutes_gol_time: number | null;
  chutes_gol_adversario: number | null;
  cartoes_amarelos_time: number | null;
  cartoes_amarelos_adversario: number | null;
  cartoes_vermelhos_time: number | null;
  cartoes_vermelhos_adversario: number | null;
}

interface Estatisticas {
  total_jogos: number;
  vitorias: number;
  empates: number;
  derrotas: number;
  gols_marcados: number;
  gols_sofridos: number;
  media_gols: number;
  sequencia_recente: string[];
}

interface Time {
  id: number;
  nome: string;
}

interface ProjecaoResumo {
  time_mandante: string;
  time_visitante: string;
  gols: { mandante: number | null; visitante: number | null };
  resultado: {
    vitoria_mandante: number | null;
    empate: number | null;
    vitoria_visitante: number | null;
  };
}

const linhasComparacao: { label: string; chave: keyof Estatisticas }[] = [
  { label: "Jogos", chave: "total_jogos" },
  { label: "Vitórias", chave: "vitorias" },
  { label: "Empates", chave: "empates" },
  { label: "Derrotas", chave: "derrotas" },
  { label: "Gols marcados", chave: "gols_marcados" },
  { label: "Gols sofridos", chave: "gols_sofridos" },
  { label: "Média de gols", chave: "media_gols" },
];

function placarArredondado(valor: number | null) {
  return valor === null || valor === undefined ? "—" : Math.round(valor);
}

function valorOuTraco(valor: number | null) {
  return valor === null || valor === undefined ? "—" : valor;
}

function percentual(valor: number | null) {
  return valor === null || valor === undefined ? "—" : valor.toFixed(2);
}

const resultadoBadge: Record<string, string> = {
  vitoria: "bg-green-500/15 text-green-400",
  empate: "bg-muted text-muted-foreground",
  derrota: "bg-red-500/15 text-red-400",
};

const resultadoInicial: Record<string, string> = {
  vitoria: "V",
  empate: "E",
  derrota: "D",
};

const resultadoFaixa: Record<string, string> = {
  vitoria: "bg-green-500",
  empate: "bg-border",
  derrota: "bg-red-500",
};

const resultadoCorQuadrado: Record<string, string> = {
  vitoria: "bg-green-600 text-white",
  empate: "bg-secondary text-secondary-foreground",
  derrota: "bg-red-600 text-white",
};

interface LinhaTabela {
  label: string;
  chave: keyof Jogo;
}

const linhasTabela: LinhaTabela[] = [
  { label: "Gols", chave: "gols_time" },
  { label: "Escanteios", chave: "escanteios_time" },
  // Em stand-by: Highlightly não fornece escanteios/chutes por tempo (1ºT/2ºT).
  // Reativar quando encontrarmos uma fonte com esse detalhamento.
  // { label: "Escanteios 1ºT", chave: "escanteios_1t_time" },
  // { label: "Escanteios 2ºT", chave: "escanteios_2t_time" },
  { label: "Chutes", chave: "chutes_time" },
  // { label: "Chutes 1ºT", chave: "chutes_1t_time" },
  { label: "Chutes ao gol", chave: "chutes_gol_time" },
  { label: "Cartões amarelos", chave: "cartoes_amarelos_time" },
  { label: "Cartões vermelhos", chave: "cartoes_vermelhos_time" },
];

function media(jogos: Jogo[], chave: keyof Jogo) {
  const valores = jogos
    .map((jogo) => jogo[chave])
    .filter((valor): valor is number => typeof valor === "number");

  if (valores.length === 0) return null;

  const soma = valores.reduce((acc, valor) => acc + valor, 0);
  return Math.round((soma / valores.length) * 10) / 10;
}

// Converte "aaaa-mm-dd" para "dd/mm/aaaa". Se o formato vier diferente, retorna a string original.
function formatarData(dataStr: string | null) {
  if (!dataStr) return "Data a definir";
  const partes = dataStr.split("-");
  if (partes.length === 3) {
    const [ano, mes, dia] = partes;
    return `${dia}/${mes}/${ano}`;
  }
  return dataStr;
}

function ListaJogos({
  jogos,
  onSelecionar,
}: {
  jogos: Jogo[];
  onSelecionar: (id: number) => void;
}) {
  return (
    <ul className="grid gap-1.5">
      {jogos.map((jogo) => (
        <li key={jogo.id}>
          <button
            type="button"
            onClick={() => onSelecionar(jogo.id)}
            className="group flex w-full items-stretch overflow-hidden rounded-md bg-card text-left ring-1 ring-foreground/10 transition-colors hover:ring-primary/40"
          >
            <span className={`w-1 shrink-0 ${resultadoFaixa[jogo.resultado] ?? "bg-border"}`} />
            <div className="min-w-0 flex-1 px-3 py-2">
              <div className="flex items-center gap-2">
                <span
                  className={`inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${resultadoBadge[jogo.resultado] ?? "bg-muted text-muted-foreground"}`}
                >
                  {resultadoInicial[jogo.resultado] ?? "?"}
                </span>
                <span className="truncate text-sm font-medium">{jogo.adversario}</span>
              </div>
              <p className="mt-0.5 pl-7 text-[11px] text-muted-foreground">
                {formatarData(jogo.data)} · {jogo.casa_ou_fora === "casa" ? "Casa" : "Fora"}
              </p>
            </div>
            <div className="relative flex w-14 shrink-0 items-center justify-center border-l border-dashed border-border bg-muted/20">
              <span className="pointer-events-none absolute -top-1.5 left-1/2 h-3 w-3 -translate-x-1/2 rounded-full bg-background" />
              <span className="font-mono text-base font-bold tabular-nums text-primary">
                {jogo.gols_time}–{jogo.gols_adversario}
              </span>
              <span className="pointer-events-none absolute -bottom-1.5 left-1/2 h-3 w-3 -translate-x-1/2 rounded-full bg-background" />
            </div>
          </button>
        </li>
      ))}
    </ul>
  );
}

function ModalEstatisticas({
  nomeTime,
  jogos,
  onFechar,
}: {
  nomeTime: string;
  jogos: Jogo[];
  onFechar: () => void;
}) {
  const cores = corTime(nomeTime);
  const larguraLabel = 108;
  const larguraMedia = 60;
  const larguraJogo = 92;
  const larguraFixa = larguraLabel + larguraMedia;
  const larguraGrade = larguraFixa + jogos.length * larguraJogo;

  return (
    <Dialog open onOpenChange={(open) => !open && onFechar()}>
      <DialogContent className="max-h-[85vh] w-auto max-w-[95vw] overflow-auto sm:max-w-[95vw]">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <span
              className={`flex size-7 shrink-0 items-center justify-center rounded-full border-2 text-[10px] font-bold ${cores.textoEscuro ? "text-black" : "text-white"}`}
              style={{ backgroundColor: cores.fundo, borderColor: cores.borda }}
            >
              {iniciais(nomeTime)}
            </span>
            <DialogTitle className="uppercase tracking-wide">
              {nomeTime} — Estatísticas Detalhadas
            </DialogTitle>
          </div>
        </DialogHeader>

        <div style={{ width: "fit-content", minWidth: larguraGrade }}>
          <div
            className="flex items-center gap-2 pb-1.5 text-[10px] font-medium uppercase tracking-wide text-muted-foreground"
            style={{ paddingLeft: larguraFixa }}
          >
            <span>Último jogo</span>
            <div className="h-px flex-1 bg-border" />
            <span>Mais antigo</span>
          </div>

          <div className="overflow-hidden rounded-lg border border-border">
            <div
              className="grid gap-px bg-border text-xs"
              style={{ gridTemplateColumns: `${larguraLabel}px ${larguraMedia}px repeat(${jogos.length}, ${larguraJogo}px)` }}
            >
              <div className="bg-card px-2 py-2" />
              <div className="border-l-2 border-primary bg-primary/10 px-2 py-2 text-center font-semibold text-primary">
                Média
              </div>
              {jogos.map((jogo, index) => (
                <div key={index} className="bg-card px-2 py-2 text-center">
                  <p className="text-[11px] text-muted-foreground">{formatarData(jogo.data)}</p>
                  <p className="mt-0.5 truncate font-medium text-foreground">{jogo.adversario}</p>
                  <span
                    className={`mt-1 inline-flex h-7 w-14 items-center justify-center rounded font-mono text-[11px] font-semibold tabular-nums ${
                      resultadoCorQuadrado[jogo.resultado] ?? "bg-secondary text-secondary-foreground"
                    }`}
                  >
                    {jogo.gols_time}x{jogo.gols_adversario}
                  </span>
                </div>
              ))}

              {linhasTabela.map((linha) => (
                <Fragment key={linha.chave}>
                  <div
                    key={`${linha.chave}-label`}
                    className="bg-background px-2 py-2 text-[11px] text-muted-foreground"
                  >
                    {linha.label}
                  </div>
                  <div
                    key={`${linha.chave}-media`}
                    className="border-l-2 border-primary bg-primary/10 px-2 py-2 text-center font-mono font-semibold tabular-nums text-primary"
                  >
                    {valorOuTraco(media(jogos, linha.chave))}
                  </div>
                  {jogos.map((jogo, index) => {
                    const valor = jogo[linha.chave];
                    return (
                      <div
                        key={`${linha.chave}-${index}`}
                        className="bg-background px-2 py-2 text-center font-mono tabular-nums text-foreground"
                      >
                        {valor === null ? "" : valor}
                      </div>
                    );
                  })}
                </Fragment>
              ))}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default function DetalheTime() {
  const params = useParams();
  const id = params.id;

  const [jogos, setJogos] = useState<Jogo[]>([]);
  const [estatisticas, setEstatisticas] =
    useState<Estatisticas | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [partidaAbertaId, setPartidaAbertaId] = useState<number | null>(null);
  const [nomeTime, setNomeTime] = useState("");
  const [quantidade, setQuantidade] = useState(10);
  const [mando, setMando] = useState<string>("todos");
  const [times, setTimes] = useState<Time[]>([]);
  const [campeonatoId, setCampeonatoId] = useState<number | null>(null);

  const [comparacaoTimeId, setComparacaoTimeId] = useState("");
  const [estatisticasComparacao, setEstatisticasComparacao] = useState<Estatisticas | null>(null);
  const [carregandoComparacao, setCarregandoComparacao] = useState(false);

  const [projecaoVisitanteId, setProjecaoVisitanteId] = useState("");
  const [projecaoRapida, setProjecaoRapida] = useState<ProjecaoResumo | null>(null);
  const [carregandoProjecaoRapida, setCarregandoProjecaoRapida] = useState(false);

  useEffect(() => {
    if (!id) return;

    setCarregando(true);
    setErro(null);

    const mandoParam = mando === "todos" ? "" : `&mando=${mando}`;

    Promise.all([
      fetch(`${API_URL}/times/${id}`).then((r) => {
        if (!r.ok) {
          throw new Error("Time não encontrado");
        }
        return r.json();
      }),

      fetch(`${API_URL}/times/${id}/jogos?quantidade=${quantidade}${mandoParam}`).then((r) => {
        if (!r.ok) {
          throw new Error("Time não encontrado ou erro ao buscar os jogos");
        }
        return r.json();
      }),

      fetch(`${API_URL}/times/${id}/estatisticas?quantidade=${quantidade}${mandoParam}`).then((r) => {
        if (!r.ok) {
          throw new Error("Time não encontrado ou erro ao buscar as estatísticas");
        }
        return r.json();
      }),
    ])
      .then(([dadosTime, dadosJogos, dadosEstatisticas]) => {
        setJogos(dadosJogos);
        setEstatisticas(dadosEstatisticas);
        setNomeTime(dadosTime.nome);

        // Lista de times pro "Comparar com"/"Projeção contra" tem que ser
        // do mesmo campeonato do time atual -- nao faz sentido comparar
        // um time da Premier League com um do Brasileirao.
        const campeonatoIdDoTime = dadosTime.campeonato_id ?? CAMPEONATO_BRASILEIRAO_ID;
        setCampeonatoId(campeonatoIdDoTime);
        return fetch(`${API_URL}/times/?campeonato_id=${campeonatoIdDoTime}`).then((r) => r.json());
      })
      .then((dadosTimes) => {
        setTimes(dadosTimes);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, [id, quantidade, mando]);

  useEffect(() => {
    if (!comparacaoTimeId) {
      setEstatisticasComparacao(null);
      return;
    }

    setCarregandoComparacao(true);

    fetch(`${API_URL}/times/${comparacaoTimeId}/estatisticas`)
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar estatísticas");
        return r.json();
      })
      .then((dados) => {
        setEstatisticasComparacao(dados);
        setCarregandoComparacao(false);
      })
      .catch(() => setCarregandoComparacao(false));
  }, [comparacaoTimeId]);

  useEffect(() => {
    if (!projecaoVisitanteId || !id) {
      setProjecaoRapida(null);
      return;
    }

    setCarregandoProjecaoRapida(true);

    fetch(`${API_URL}/projecoes/${id}/${projecaoVisitanteId}`)
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar projeção");
        return r.json();
      })
      .then((dados) => {
        setProjecaoRapida(dados);
        setCarregandoProjecaoRapida(false);
      })
      .catch(() => setCarregandoProjecaoRapida(false));
  }, [projecaoVisitanteId, id]);

  if (carregando) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <VhSpinner />
      </main>
    );
  }

  if (erro) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background text-destructive">
        <p>Erro: {erro}</p>
        <Link
          href="/times"
          className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Voltar para a lista de times
        </Link>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-6 py-10 text-foreground">
      <div className="mx-auto max-w-2xl">
        <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
          <Link
            href={
              campeonatoId && campeonatoId !== CAMPEONATO_BRASILEIRAO_ID
                ? `/times?campeonato=${campeonatoId}`
                : "/times"
            }
            className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
            Times
          </Link>
          <div className="flex gap-2">
            <NavChip href={`/comparar?time=${id}`} label="Comparar" icon={Users} cor="rose" />
            <NavChip href={`/previsao?mandante=${id}`} label="Projeção" icon={TrendingUp} cor="gold" />
            <NavChip href={`/times/${id}/jogadores`} label="Jogadores" icon={BarChart3} cor="violet" />
          </div>
        </div>

        <div className="mt-4 flex items-center gap-3">
          {(() => {
            const cores = corTime(nomeTime);
            return (
              <span
                className={`flex size-11 shrink-0 items-center justify-center rounded-full border-2 text-sm font-bold ${cores.textoEscuro ? "text-black" : "text-white"}`}
                style={{ backgroundColor: cores.fundo, borderColor: cores.borda }}
              >
                {iniciais(nomeTime)}
              </span>
            );
          })()}
          <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
            {nomeTime}
          </h1>
        </div>

        <div className="mt-6 flex items-center justify-between">
          <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Período de análise
          </h2>
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
        </div>

        <div className="mt-3 flex items-center justify-between">
          <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Mando de campo
          </h2>
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

        {estatisticas && (
          <div className="mt-3 overflow-hidden rounded-lg border border-border bg-card">
            <div className="grid grid-cols-4 divide-x divide-border text-center">
              <div className="px-2 py-3">
                <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">J</p>
                <p className="mt-0.5 font-mono text-lg font-bold tabular-nums">{estatisticas.total_jogos}</p>
              </div>
              <div className="px-2 py-3">
                <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">V</p>
                <p className="mt-0.5 font-mono text-lg font-bold tabular-nums text-green-400">{estatisticas.vitorias}</p>
              </div>
              <div className="px-2 py-3">
                <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">E</p>
                <p className="mt-0.5 font-mono text-lg font-bold tabular-nums text-muted-foreground">{estatisticas.empates}</p>
              </div>
              <div className="px-2 py-3">
                <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">D</p>
                <p className="mt-0.5 font-mono text-lg font-bold tabular-nums text-red-400">{estatisticas.derrotas}</p>
              </div>
            </div>

            <div className="border-t border-border px-4 py-2.5 text-center text-xs text-muted-foreground">
              Gols marcados <span className="font-mono font-medium text-foreground">{estatisticas.gols_marcados}</span>
              <span className="mx-2 text-border">·</span>
              Gols sofridos <span className="font-mono font-medium text-foreground">{estatisticas.gols_sofridos}</span>
              <span className="mx-2 text-border">·</span>
              Média <span className="font-mono font-medium text-primary">{estatisticas.media_gols}</span>
            </div>

            {estatisticas.sequencia_recente.length > 0 && (
              <div className="border-t border-border px-4 py-2.5">
                <div className="flex flex-wrap items-center justify-center gap-1.5">
                  <span className="mr-1 text-[10px] uppercase tracking-[0.15em] text-muted-foreground">Forma</span>
                  {estatisticas.sequencia_recente.map((resultado, i) => (
                    <span
                      key={i}
                      className={`flex size-5 items-center justify-center rounded-full text-[10px] font-bold ${resultadoBadge[resultado] ?? "bg-muted text-muted-foreground"}`}
                    >
                      {resultadoInicial[resultado] ?? "?"}
                    </span>
                  ))}
                </div>
                <p className="mt-1.5 text-center text-[9px] uppercase tracking-wide text-muted-foreground">
                  Último jogo → Mais antigo
                </p>
              </div>
            )}
          </div>
        )}

        <div className="mt-8">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="flex size-6 shrink-0 items-center justify-center rounded-md bg-rose-500/10 text-rose-400">
                <Users className="size-3.5" />
              </span>
              <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Comparar com
              </h2>
            </div>
            <select
              value={comparacaoTimeId}
              onChange={(e) => setComparacaoTimeId(e.target.value)}
              className="rounded-lg border border-input bg-card px-3 py-1.5 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="">Selecione um time</option>
              {times
                .filter((t) => t.id !== Number(id))
                .map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.nome}
                  </option>
                ))}
            </select>
          </div>

          {carregandoComparacao && (
            <div className="mt-3 flex min-h-24 items-center justify-center">
              <VhSpinner />
            </div>
          )}

          {estatisticasComparacao && estatisticas && !carregandoComparacao && (
            <div className="mt-3 overflow-hidden rounded-lg border border-border">
              <div className="grid grid-cols-3 bg-card px-4 py-2 text-xs font-semibold">
                <span className="text-foreground">{nomeTime}</span>
                <span className="text-center text-muted-foreground">Estatística</span>
                <span className="text-right text-foreground">
                  {times.find((t) => t.id === Number(comparacaoTimeId))?.nome}
                </span>
              </div>
              {linhasComparacao.map((linha) => {
                const valorA = estatisticas[linha.chave];
                const valorB = estatisticasComparacao[linha.chave];
                const aMaior = typeof valorA === "number" && typeof valorB === "number" && valorA > valorB;
                const bMaior = typeof valorA === "number" && typeof valorB === "number" && valorB > valorA;
                return (
                  <div
                    key={linha.chave}
                    className="grid grid-cols-3 border-t border-border px-4 py-2 text-sm"
                  >
                    <span
                      className={`font-mono tabular-nums ${aMaior ? "font-semibold text-primary" : "text-muted-foreground"}`}
                    >
                      {Array.isArray(valorA) ? "" : valorA}
                    </span>
                    <span className="text-center text-muted-foreground">{linha.label}</span>
                    <span
                      className={`text-right font-mono tabular-nums ${bMaior ? "font-semibold text-primary" : "text-muted-foreground"}`}
                    >
                      {Array.isArray(valorB) ? "" : valorB}
                    </span>
                  </div>
                );
              })}
              <div className="border-t border-border bg-card px-4 py-2 text-center">
                <Link
                  href={`/comparar?time=${id}&timeB=${comparacaoTimeId}`}
                  className="inline-flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-primary"
                >
                  Ver comparação completa
                  <ChevronRight className="size-3" />
                </Link>
              </div>
            </div>
          )}
        </div>

        <div className="mt-8">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="flex size-6 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                <TrendingUp className="size-3.5" />
              </span>
              <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Projeção contra
              </h2>
            </div>
            <select
              value={projecaoVisitanteId}
              onChange={(e) => setProjecaoVisitanteId(e.target.value)}
              className="rounded-lg border border-input bg-card px-3 py-1.5 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="">Selecione um time</option>
              {times
                .filter((t) => t.id !== Number(id))
                .map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.nome}
                  </option>
                ))}
            </select>
          </div>

          {carregandoProjecaoRapida && (
            <div className="mt-3 flex min-h-28 items-center justify-center rounded-lg border border-border">
              <VhSpinner />
            </div>
          )}

          {projecaoRapida && !carregandoProjecaoRapida && (
            <div className="mt-3 rounded-lg border border-primary/30 bg-primary/5 p-4 text-center">
              <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3">
                <span className="truncate text-right font-heading text-xs uppercase tracking-wide">
                  {projecaoRapida.time_mandante}
                </span>
                <span className="font-mono text-xl font-bold tabular-nums text-primary">
                  {placarArredondado(projecaoRapida.gols.mandante)}–{placarArredondado(projecaoRapida.gols.visitante)}
                </span>
                <span className="truncate text-left font-heading text-xs uppercase tracking-wide">
                  {projecaoRapida.time_visitante}
                </span>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                <p className="font-mono font-semibold tabular-nums text-muted-foreground">
                  {percentual(projecaoRapida.resultado.vitoria_mandante)}%
                </p>
                <p className="font-mono font-semibold tabular-nums text-muted-foreground">
                  {percentual(projecaoRapida.resultado.empate)}%{" "}
                  <span className="block text-[10px] font-normal">Empate</span>
                </p>
                <p className="font-mono font-semibold tabular-nums text-muted-foreground">
                  {percentual(projecaoRapida.resultado.vitoria_visitante)}%
                </p>
              </div>
              <Link
                href={`/previsao?mandante=${id}&visitante=${projecaoVisitanteId}`}
                className="mt-3 inline-flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-primary"
              >
                Ver projeção completa
                <ChevronRight className="size-3" />
              </Link>
            </div>
          )}
        </div>

        <div className="mt-8 flex items-center justify-between">
          <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Últimos Jogos
          </h2>
          {jogos.length > 0 && (
            <button
              onClick={() => setModalAberto(true)}
              className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-muted"
            >
              Ver estatísticas detalhadas
            </button>
          )}
        </div>

        <p className="mt-1 text-xs text-muted-foreground">Toque em um jogo para ver os detalhes.</p>

        <div className="mt-4">
          <ListaJogos jogos={jogos} onSelecionar={setPartidaAbertaId} />
        </div>
      </div>

      {modalAberto && (
        <ModalEstatisticas
          nomeTime={nomeTime}
          jogos={jogos}
          onFechar={() => setModalAberto(false)}
        />
      )}

      <PartidaModal partidaId={partidaAbertaId} onClose={() => setPartidaAbertaId(null)} />
    </main>
  );
}
