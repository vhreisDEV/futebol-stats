"use client";

import { useEffect, useState } from "react";

interface Time {
  id: number;
  nome: string;
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

export default function CompararTimes() {
  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const [timeAId, setTimeAId] = useState<string>("");
  const [timeBId, setTimeBId] = useState<string>("");

  const [estatisticasA, setEstatisticasA] = useState<Estatisticas | null>(null);
  const [estatisticasB, setEstatisticasB] = useState<Estatisticas | null>(null);
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
    ])
      .then(([dadosA, dadosB]) => {
        setEstatisticasA(dadosA);
        setEstatisticasB(dadosB);
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
        <h1 className="text-3xl font-bold tracking-tight">
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
      </div>
    </main>
  );
}