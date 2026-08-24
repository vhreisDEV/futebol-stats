"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { PartidaModal } from "@/components/partida-modal";
import { VhSpinner } from "@/components/vh-spinner";
import { API_URL, CAMPEONATO_BRASILEIRAO_ID } from "@/lib/api";

interface Time {
  id: number;
  nome: string;
}

interface Jogo {
  id: number;
  data: string | null;
  adversario: string;
  casa_ou_fora: string;
  resultado: string;
  gols_time: number;
  gols_adversario: number;
}

interface Estatisticas {
  total_jogos: number;
  vitorias: number;
  empates: number;
  derrotas: number;
  gols_marcados: number;
  gols_sofridos: number;
  media_gols: number;
  media_escanteios: number;
  media_chutes: number;
  media_chutes_gol: number;
  media_cartoes_amarelos: number;
  media_cartoes_vermelhos: number;
  sequencia_recente: string[];
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

function CompararTimesConteudo() {
  const searchParams = useSearchParams();
  const timePreSelecionado = searchParams.get("time") ?? "";
  const timeBPreSelecionado = searchParams.get("timeB") ?? "";

  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const [timeAId, setTimeAId] = useState<string>(timePreSelecionado);
  const [timeBId, setTimeBId] = useState<string>(timeBPreSelecionado);
  const [quantidade, setQuantidade] = useState(10);

  const [estatisticasA, setEstatisticasA] = useState<Estatisticas | null>(null);
  const [estatisticasB, setEstatisticasB] = useState<Estatisticas | null>(null);
  const [jogosA, setJogosA] = useState<Jogo[]>([]);
  const [jogosB, setJogosB] = useState<Jogo[]>([]);
  const [carregandoComparacao, setCarregandoComparacao] = useState(false);
  const [erroComparacao, setErroComparacao] = useState<string | null>(null);
  const [partidaAbertaId, setPartidaAbertaId] = useState<number | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/times/?campeonato_id=${CAMPEONATO_BRASILEIRAO_ID}`)
      .then((resposta) => {
        if (!resposta.ok) {
          throw new Error("Erro ao buscar times");
        }
        return resposta.json();
      })
      .then((dados) => {
        setTimes(dados);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, []);

  useEffect(() => {
    if (!timeAId || !timeBId) {
      setEstatisticasA(null);
      setEstatisticasB(null);
      setJogosA([]);
      setJogosB([]);
      return;
    }

    if (timeAId === timeBId) {
      setEstatisticasA(null);
      setEstatisticasB(null);
      setJogosA([]);
      setJogosB([]);
      return;
    }

    setCarregandoComparacao(true);
    setErroComparacao(null);

    Promise.all([
      fetch(`${API_URL}/times/${timeAId}/estatisticas?quantidade=${quantidade}`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar estatísticas do Time A");
        return r.json();
      }),
      fetch(`${API_URL}/times/${timeBId}/estatisticas?quantidade=${quantidade}`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar estatísticas do Time B");
        return r.json();
      }),
      fetch(`${API_URL}/times/${timeAId}/jogos?quantidade=${quantidade}`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar jogos do Time A");
        return r.json();
      }),
      fetch(`${API_URL}/times/${timeBId}/jogos?quantidade=${quantidade}`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar jogos do Time B");
        return r.json();
      }),
    ])
      .then(([dadosEstA, dadosEstB, dadosJogosA, dadosJogosB]) => {
        setEstatisticasA(dadosEstA);
        setEstatisticasB(dadosEstB);
        setJogosA(dadosJogosA);
        setJogosB(dadosJogosB);
        setCarregandoComparacao(false);
      })
      .catch((err) => {
        setErroComparacao(err.message);
        setCarregandoComparacao(false);
      });
  }, [timeAId, timeBId, quantidade]);

  if (carregando) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <VhSpinner />
      </main>
    );
  }

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-destructive">
        <p>Erro: {erro}</p>
      </main>
    );
  }

  const timeA = times.find((t) => t.id === Number(timeAId));
  const timeB = times.find((t) => t.id === Number(timeBId));

  const linhas: { label: string; chave: keyof Estatisticas }[] = [
    { label: "Jogos", chave: "total_jogos" },
    { label: "Vitórias", chave: "vitorias" },
    { label: "Empates", chave: "empates" },
    { label: "Derrotas", chave: "derrotas" },
    { label: "Gols marcados", chave: "gols_marcados" },
    { label: "Gols sofridos", chave: "gols_sofridos" },
    { label: "Média de gols", chave: "media_gols" },
    { label: "Escanteios (média)", chave: "media_escanteios" },
    { label: "Chutes (média)", chave: "media_chutes" },
    { label: "Chutes ao gol (média)", chave: "media_chutes_gol" },
    { label: "Cartões amarelos (média)", chave: "media_cartoes_amarelos" },
    { label: "Cartões vermelhos (média)", chave: "media_cartoes_vermelhos" },
  ];

  return (
    <main className="min-h-screen bg-background px-6 py-10 text-foreground">
      <div className="mx-auto max-w-3xl">
        <Link
          href="/brasileirao"
          className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Brasileirão
        </Link>

        <h1 className="mt-4 font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
          Comparar Times
        </h1>
        <p className="mt-2 text-muted-foreground">
          Selecione dois times para comparar suas estatísticas.
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          Considera apenas jogos do Brasileirão Série A — os times também disputam outras
          competições (Copa do Brasil, Libertadores, Sul-Americana etc.), que não entram nesta
          conta. Os números somam jogos dentro e fora de casa.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm text-muted-foreground">
              Time A
            </label>
            <select
              value={timeAId}
              onChange={(e) => setTimeAId(e.target.value)}
              className="w-full rounded-lg border border-input bg-card px-4 py-2 text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="">Selecione um time</option>
              {times.map((time) => (
                <option key={time.id} value={time.id}>
                  {time.nome}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm text-muted-foreground">
              Time B
            </label>
            <select
              value={timeBId}
              onChange={(e) => setTimeBId(e.target.value)}
              className="w-full rounded-lg border border-input bg-card px-4 py-2 text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="">Selecione um time</option>
              {times.map((time) => (
                <option key={time.id} value={time.id}>
                  {time.nome}
                </option>
              ))}
            </select>
          </div>
        </div>

        {timeAId && timeBId && timeAId !== timeBId && (
          <div className="mt-4 flex items-center justify-between gap-3">
            <span className="text-sm text-muted-foreground">Período de análise</span>
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
        )}

        {timeAId && timeBId && timeAId === timeBId && (
          <p className="mt-8 text-primary">
            Selecione dois times diferentes para comparar.
          </p>
        )}

        {carregandoComparacao && (
          <div className="mt-8 flex min-h-24 items-center justify-center">
            <VhSpinner />
          </div>
        )}

        {erroComparacao && (
          <p className="mt-8 text-destructive">Erro: {erroComparacao}</p>
        )}

        {estatisticasA && estatisticasB && timeA && timeB && (
          <div className="mt-8 overflow-hidden rounded-lg border border-border">
            <div className="grid grid-cols-3 bg-card px-4 py-3 text-sm font-semibold">
              <span className="text-foreground">{timeA.nome}</span>
              <span className="text-center text-muted-foreground">Estatística</span>
              <span className="text-right text-foreground">{timeB.nome}</span>
            </div>

            {linhas.map((linha) => {
              const valorA = estatisticasA[linha.chave];
              const valorB = estatisticasB[linha.chave];
              const aMaior = typeof valorA === "number" && typeof valorB === "number" && valorA > valorB;
              const bMaior = typeof valorA === "number" && typeof valorB === "number" && valorB > valorA;

              return (
                <div
                  key={linha.chave}
                  className="grid grid-cols-3 border-t border-border px-4 py-3 text-sm"
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
          </div>
        )}

        {jogosA.length > 0 && jogosB.length > 0 && timeA && timeB && (
          <div className="mt-10">
            <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Últimos Jogos
            </h2>
            <p className="mt-1 text-xs text-muted-foreground">Toque em um jogo para ver os detalhes.</p>
            <div className="mt-4 grid gap-6 sm:grid-cols-2">
              <div>
                <p className="mb-2 text-sm font-medium text-muted-foreground">{timeA.nome}</p>
                <ListaJogos jogos={jogosA} onSelecionar={setPartidaAbertaId} />
              </div>
              <div>
                <p className="mb-2 text-sm font-medium text-muted-foreground">{timeB.nome}</p>
                <ListaJogos jogos={jogosB} onSelecionar={setPartidaAbertaId} />
              </div>
            </div>
          </div>
        )}
      </div>

      <PartidaModal partidaId={partidaAbertaId} onClose={() => setPartidaAbertaId(null)} />
    </main>
  );
}

export default function CompararTimes() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
          <p>Carregando...</p>
        </main>
      }
    >
      <CompararTimesConteudo />
    </Suspense>
  );
}
