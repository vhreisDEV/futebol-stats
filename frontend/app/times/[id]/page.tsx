"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

interface Jogo {
  data: string;
  adversario: string;
  casa_ou_fora: string;
  resultado: string;
  gols_time: number;
  gols_adversario: number;
  escanteios_time: number;
  escanteios_adversario: number;
  escanteios_1t_time: number;
  escanteios_1t_adversario: number;
  escanteios_2t_time: number;
  escanteios_2t_adversario: number;
  chutes_time: number;
  chutes_adversario: number;
  chutes_1t_time: number;
  chutes_1t_adversario: number;
  chutes_gol_time: number;
  chutes_gol_adversario: number;
  cartoes_amarelos_time: number;
  cartoes_amarelos_adversario: number;
  cartoes_vermelhos_time: number;
  cartoes_vermelhos_adversario: number;
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

const resultadoEstilo: Record<string, string> = {
  vitoria: "border-l-4 border-green-500 bg-green-500/10",
  empate: "border-l-4 border-border bg-card",
  derrota: "border-l-4 border-red-500 bg-red-500/10",
};

const resultadoLabel: Record<string, string> = {
  vitoria: "Vitória",
  empate: "Empate",
  derrota: "Derrota",
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
  { label: "Escanteios 1ºT", chave: "escanteios_1t_time" },
  { label: "Escanteios 2ºT", chave: "escanteios_2t_time" },
  { label: "Chutes", chave: "chutes_time" },
  { label: "Chutes 1ºT", chave: "chutes_1t_time" },
  { label: "Chutes ao gol", chave: "chutes_gol_time" },
  { label: "Cartões amarelos", chave: "cartoes_amarelos_time" },
  { label: "Cartões vermelhos", chave: "cartoes_vermelhos_time" },
];

function media(jogos: Jogo[], chave: keyof Jogo) {
  if (jogos.length === 0) return 0;
  const soma = jogos.reduce((acc, jogo) => acc + Number(jogo[chave]), 0);
  return Math.round((soma / jogos.length) * 10) / 10;
}

// Converte "aaaa-mm-dd" para "dd/mm/aaaa". Se o formato vier diferente, retorna a string original.
function formatarData(dataStr: string) {
  const partes = dataStr.split("-");
  if (partes.length === 3) {
    const [ano, mes, dia] = partes;
    return `${dia}/${mes}/${ano}`;
  }
  return dataStr;
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
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4"
      onClick={onFechar}
    >
      <div
        className="max-h-[85vh] w-full max-w-5xl overflow-auto rounded-lg border border-border bg-popover p-5"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-heading text-base font-semibold uppercase tracking-wide text-foreground">
            {nomeTime} — Estatísticas Detalhadas
          </h2>
          <button
            onClick={onFechar}
            className="rounded-md border border-border px-3 py-1 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            Fechar
          </button>
        </div>

        <div className="min-w-[700px]">
          <div
            className="grid gap-px text-xs"
            style={{ gridTemplateColumns: `160px 100px repeat(${jogos.length}, 100px)` }}
          >
            <div className="bg-muted/40 px-2 py-2" />
            <div className="border-l-2 border-primary bg-primary/10 px-2 py-2 text-center font-semibold text-primary">
              Média
            </div>
            {jogos.map((jogo, index) => (
              <div key={index} className="bg-muted/40 px-2 py-2 text-center">
                <p className="text-[11px] text-muted-foreground">{formatarData(jogo.data)}</p>
                <p className="mt-0.5 font-medium text-foreground">
                  {jogo.casa_ou_fora === "casa" ? "vs" : "@"} {jogo.adversario}
                </p>
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
              <>
                <div
                  key={`${linha.chave}-label`}
                  className="bg-muted/20 px-2 py-2 text-muted-foreground"
                >
                  {linha.label}
                </div>
                <div
                  key={`${linha.chave}-media`}
                  className="border-l-2 border-primary bg-primary/10 px-2 py-2 text-center font-mono font-semibold tabular-nums text-primary"
                >
                  {media(jogos, linha.chave)}
                </div>
                {jogos.map((jogo, index) => (
                  <div
                    key={`${linha.chave}-${index}`}
                    className="bg-muted/20 px-2 py-2 text-center font-mono tabular-nums text-foreground"
                  >
                    {jogo[linha.chave]}
                  </div>
                ))}
              </>
            ))}
          </div>
        </div>
      </div>
    </div>
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
  const [nomeTime, setNomeTime] = useState("");
  const [quantidade, setQuantidade] = useState(10);

  useEffect(() => {
    if (!id) return;

    setCarregando(true);
    setErro(null);

    Promise.all([
      fetch(`http://127.0.0.1:8000/times/${id}/jogos?quantidade=${quantidade}`).then((r) => {
        if (!r.ok) {
          throw new Error("Time não encontrado ou erro ao buscar os jogos");
        }
        return r.json();
      }),

      fetch(`http://127.0.0.1:8000/times/${id}/estatisticas?quantidade=${quantidade}`).then((r) => {
        if (!r.ok) {
          throw new Error("Time não encontrado ou erro ao buscar as estatísticas");
        }
        return r.json();
      }),

      fetch(`http://127.0.0.1:8000/times/`).then((r) => r.json()),
    ])
      .then(([dadosJogos, dadosEstatisticas, dadosTimes]) => {
        setJogos(dadosJogos);
        setEstatisticas(dadosEstatisticas);
        const timeAtual = dadosTimes.find((t: { id: number; nome: string }) => t.id === Number(id));
        setNomeTime(timeAtual ? timeAtual.nome : "Time");
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, [id, quantidade]);

  if (carregando) {
    return (
      <main className="min-h-screen bg-background px-6 py-10 text-foreground">
        <div className="mx-auto max-w-2xl">
          <Skeleton className="h-4 w-40" />
          <Skeleton className="mt-4 h-8 w-56" />
          <Skeleton className="mt-6 h-32 w-full rounded-lg" />
          <Skeleton className="mt-8 h-4 w-32" />
          <div className="mt-4 grid gap-2">
            <Skeleton className="h-14 w-full rounded-md" />
            <Skeleton className="h-14 w-full rounded-md" />
            <Skeleton className="h-14 w-full rounded-md" />
          </div>
        </div>
      </main>
    );
  }

  if (erro) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background text-destructive">
        <p>Erro: {erro}</p>
        <Link href="/times" className="text-muted-foreground underline hover:text-primary">
          Voltar para a lista de times
        </Link>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-6 py-10 text-foreground">
      <div className="mx-auto max-w-2xl">
        <div className="flex items-center justify-between">
          <Link
            href="/times"
            className="text-sm text-muted-foreground underline hover:text-primary"
          >
            ← Voltar para a lista de times
          </Link>
          <div className="flex gap-4">
            <Link
              href={`/comparar?time=${id}`}
              className="text-sm text-muted-foreground underline hover:text-primary"
            >
              Comparar
            </Link>
            <Link
              href={`/projecao?mandante=${id}`}
              className="text-sm text-muted-foreground underline hover:text-primary"
            >
              Projeção
            </Link>
          </div>
        </div>

        <h1 className="mt-4 font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
          {nomeTime}
        </h1>

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
          </ToggleGroup>
        </div>

        {estatisticas && (
          <div className="mt-3 rounded-lg border border-border bg-card p-5">
            <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Estatísticas
            </h2>
            <div className="mt-4 grid grid-cols-2 gap-y-2 text-sm sm:grid-cols-3">
              <p className="text-muted-foreground">
                Jogos: <span className="font-medium text-foreground">{estatisticas.total_jogos}</span>
              </p>
              <p className="text-green-400">
                Vitórias: <span className="font-medium">{estatisticas.vitorias}</span>
              </p>
              <p className="text-muted-foreground">
                Empates: <span className="font-medium text-foreground">{estatisticas.empates}</span>
              </p>
              <p className="text-red-400">
                Derrotas: <span className="font-medium">{estatisticas.derrotas}</span>
              </p>
              <p className="text-muted-foreground">
                Gols marcados: <span className="font-medium text-foreground">{estatisticas.gols_marcados}</span>
              </p>
              <p className="text-muted-foreground">
                Gols sofridos: <span className="font-medium text-foreground">{estatisticas.gols_sofridos}</span>
              </p>
              <p className="text-muted-foreground col-span-2 sm:col-span-3">
                Média de gols por jogo:{" "}
                <span className="font-mono font-medium tabular-nums text-primary">
                  {estatisticas.media_gols}
                </span>
              </p>
            </div>
          </div>
        )}

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

        <ul className="mt-4 grid gap-2">
          {jogos.map((jogo, index) => (
            <li
              key={index}
              onClick={() => setModalAberto(true)}
              className={`cursor-pointer rounded-md px-4 py-3 text-sm transition hover:opacity-80 ${resultadoEstilo[jogo.resultado] ?? "border-l-4 border-border bg-card"}`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">
                  {jogo.casa_ou_fora === "casa" ? "vs" : "@"} {jogo.adversario}
                </span>
                <span className="text-muted-foreground">{formatarData(jogo.data)}</span>
              </div>
              <div className="mt-1 flex items-center justify-between text-muted-foreground">
                <span className="font-mono tabular-nums text-foreground">
                  {jogo.gols_time}x{jogo.gols_adversario}
                </span>
                <span>{resultadoLabel[jogo.resultado] ?? jogo.resultado}</span>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {modalAberto && (
        <ModalEstatisticas
          nomeTime={nomeTime}
          jogos={jogos}
          onFechar={() => setModalAberto(false)}
        />
      )}
    </main>
  );
}
