"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Time {
  id: number;
  nome: string;
}

export default function Home() {
  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

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

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 px-6 py-10">
      <div className="mx-auto max-w-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Football Analytics Platform
            </h1>
            <p className="mt-2 text-slate-400">
              Selecione um time para ver os últimos jogos e estatísticas.
            </p>
          </div>
          <div className="flex shrink-0 flex-col gap-2 sm:flex-row">
            <Link
              href="/comparar"
              className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-center text-sm font-medium text-slate-100 transition hover:border-slate-600 hover:bg-slate-800"
            >
              Comparar Times
            </Link>
            <Link
              href="/projecao"
              className="rounded-lg border border-indigo-800 bg-indigo-950/40 px-4 py-2 text-center text-sm font-medium text-slate-100 transition hover:border-indigo-600 hover:bg-indigo-900/40"
            >
              Projeção Pré-Jogo
            </Link>
          </div>
        </div>

        <div className="mt-8 grid gap-3">
          {times.map((time) => (
            <Link
              key={time.id}
              href={`/times/${time.id}`}
              className="rounded-lg border border-slate-800 bg-slate-900 px-5 py-4 font-medium text-slate-100 transition hover:border-slate-600 hover:bg-slate-800"
            >
              {time.nome}
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
