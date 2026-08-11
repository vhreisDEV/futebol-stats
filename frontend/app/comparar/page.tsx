"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Time {
  id: number;
  nome: string;
}

interface Jogo {
  data: string;
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
  sequencia_recente: string[];
}

const resultadoEstilo: Record<string, string> = {
  vitoria: "border-l-4 border-green-500 bg-green-950/40",
  empate: "border-l-4 border-slate-500 bg-slate-800/60",
  derrota: "border-l-4 border-red-500 bg-red-950/40",
};

const resultadoLabel: Record<string, string> = {
  vitoria: "Vitória",
  empate: "Empate",
  derrota: "Derrota",
};

function ListaJogos({ jogos }: { jogos: Jogo[] }) {
  return (
    <ul className="grid gap-2">
      {jogos.map((jogo, index) => (
        <li
          key={index}
          className={`rounded-md px-3 py-2 text-sm ${resultadoEstilo[jogo.resultado] ?? "border-l-4 border-slate-700 bg-slate-900"}`}
        >
          <div className="flex items-center justify-between">
            <span className="font-medium">
              {jogo.casa_ou_fora === "casa" ? "vs" : "@"} {jogo.adversario}
            </span>
            <span className="text-slate-400">{jogo.data}</span>
          </div>
          <div className="mt-1 flex items-center justify-between text-slate-300">
            <span>{jogo.gols_time}x{jogo.gols_adversario}</span>
            <span>{resultadoLabel[jogo.resultado] ?? jogo.resultado}</span>
          </div>
        </li>
      ))}
    </ul>
  );
}

export default function CompararTimes() {
  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const [timeAId, setTimeAId] = useState<string>("");
  const [timeBId, setTimeBId] = useState<string>("");

  const [estatisticasA, setEstatisticasA] = useState<Estatisticas | null>(null);
  const [estatisticasB, setEstatisticasB] = useState<Estatisticas | null>(null);
  const [jogosA, setJogosA] = useState<Jogo[]>([]);
  const [jogosB, setJogosB] = useState<Jogo[]>([]);
  const [carregandoComparacao, setCarregandoComparacao] = useState(false);
  const [erroComparacao, setErroComparacao] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/times/")
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
      fetch(`http://127.0.0.1:8000/times/${timeAId}/estatisticas`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar estatísticas do Time A");
        return r.json();
      }),
      fetch(`http://127.0.0.1:8000/times/${timeBId}/estatisticas`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar estatísticas do Time B");
        return r.json();
      }),
      fetch(`http://127.0.0.1:8000/times/${timeAId}/jogos`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar jogos do Time A");
        return r.json();
      }),
      fetch(`http://127.0.0.1:8000/times/${timeBId}/jogos`).then((r) => {
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
  }, [timeAId, timeBId]);

  if (carregando) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-300">
        <p>Carregando times...</p>
      </main>
    );
  }

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-red-400">
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
  ];

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-3xl">
        <Link
          href="/"
          className="text-sm text-slate-400 underline hover:text-white"
        >
          ← Voltar para a lista de times
        </Link>

        <h1 className="mt-4 text-3xl font-bold tracking-tight">
          Comparar Times
        </h1>
        <p className="mt-2 text-slate-400">
          Selecione dois times para comparar suas estatísticas.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm text-slate-400">
              Time A
            </label>
            <select
              value={timeAId}
              onChange={(e) => setTimeAId(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-slate-100"
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
            <label className="mb-2 block text-sm text-slate-400">
              Time B
            </label>
            <select
              value={timeBId}
              onChange={(e) => setTimeBId(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-slate-100"
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

        {timeAId && timeBId && timeAId === timeBId && (
          <p className="mt-8 text-amber-400">
            Selecione dois times diferentes para comparar.
          </p>
        )}

        {carregandoComparacao && (
          <p className="mt-8 text-slate-400">Carregando comparação...</p>
        )}

        {erroComparacao && (
          <p className="mt-8 text-red-400">Erro: {erroComparacao}</p>
        )}

        {estatisticasA && estatisticasB && timeA && timeB && (
          <div className="mt-8 overflow-hidden rounded-lg border border-slate-800">
            <div className="grid grid-cols-3 bg-slate-900 px-4 py-3 text-sm font-semibold">
              <span className="text-white">{timeA.nome}</span>
              <span className="text-center text-slate-500">Estatística</span>
              <span className="text-right text-white">{timeB.nome}</span>
            </div>

            {linhas.map((linha) => {
              const valorA = estatisticasA[linha.chave];
              const valorB = estatisticasB[linha.chave];
              const aMaior = typeof valorA === "number" && typeof valorB === "number" && valorA > valorB;
              const bMaior = typeof valorA === "number" && typeof valorB === "number" && valorB > valorA;

              return (
                <div
                  key={linha.chave}
                  className="grid grid-cols-3 border-t border-slate-800 px-4 py-3 text-sm"
                >
                  <span className={aMaior ? "font-semibold text-green-400" : "text-slate-300"}>
                    {Array.isArray(valorA) ? "" : valorA}
                  </span>
                  <span className="text-center text-slate-500">{linha.label}</span>
                  <span className={`text-right ${bMaior ? "font-semibold text-green-400" : "text-slate-300"}`}>
                    {Array.isArray(valorB) ? "" : valorB}
                  </span>
                </div>
              );
            })}
          </div>
        )}

        {jogosA.length > 0 && jogosB.length > 0 && timeA && timeB && (
          <div className="mt-10">
            <h2 className="text-lg font-semibold">Últimos Jogos</h2>
            <div className="mt-4 grid gap-6 sm:grid-cols-2">
              <div>
                <p className="mb-2 text-sm font-medium text-slate-400">{timeA.nome}</p>
                <ListaJogos jogos={jogosA} />
              </div>
              <div>
                <p className="mb-2 text-sm font-medium text-slate-400">{timeB.nome}</p>
                <ListaJogos jogos={jogosB} />
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}