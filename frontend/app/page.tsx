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
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Football Analytics Platform
            </h1>
            <p className="mt-2 text-slate-400">
              Selecione um time para ver os últimos jogos e estatísticas.
            </p>
          </div>
          <Link
            href="/comparar"
            className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-100 transition hover:border-slate-600 hover:bg-slate-800"
          >
            Comparar Times
          </Link>
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