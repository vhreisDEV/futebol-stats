"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

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

export default function DetalheTime() {
  const params = useParams();
  const id = params.id;

  const [jogos, setJogos] = useState<Jogo[]>([]);
  const [estatisticas, setEstatisticas] =
    useState<Estatisticas | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    setCarregando(true);
    setErro(null);

    Promise.all([
      fetch(`http://127.0.0.1:8000/times/${id}/jogos`).then((r) => {
        if (!r.ok) {
          throw new Error("Time não encontrado ou erro ao buscar os jogos");
        }
        return r.json();
      }),

      fetch(`http://127.0.0.1:8000/times/${id}/estatisticas`).then((r) => {
        if (!r.ok) {
          throw new Error("Time não encontrado ou erro ao buscar as estatísticas");
        }
        return r.json();
      }),
    ])
      .then(([dadosJogos, dadosEstatisticas]) => {
        setJogos(dadosJogos);
        setEstatisticas(dadosEstatisticas);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, [id]);

  if (carregando) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-300">
        <p>Carregando...</p>
      </main>
    );
  }

  if (erro) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-950 text-red-400">
        <p>Erro: {erro}</p>
        <Link href="/" className="text-slate-300 underline hover:text-white">
          Voltar para a lista de times
        </Link>
      </main>
    );
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

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-2xl">
        <Link
          href="/"
          className="text-sm text-slate-400 underline hover:text-white"
        >
          ← Voltar para a lista de times
        </Link>

        {estatisticas && (
          <div className="mt-6 rounded-lg border border-slate-800 bg-slate-900 p-5">
            <h2 className="text-lg font-semibold">Estatísticas</h2>
            <div className="mt-4 grid grid-cols-2 gap-y-2 text-sm sm:grid-cols-3">
              <p className="text-slate-300">
                Jogos: <span className="font-medium text-white">{estatisticas.total_jogos}</span>
              </p>
              <p className="text-green-400">
                Vitórias: <span className="font-medium">{estatisticas.vitorias}</span>
              </p>
              <p className="text-slate-300">
                Empates: <span className="font-medium">{estatisticas.empates}</span>
              </p>
              <p className="text-red-400">
                Derrotas: <span className="font-medium">{estatisticas.derrotas}</span>
              </p>
              <p className="text-slate-300">
                Gols marcados: <span className="font-medium text-white">{estatisticas.gols_marcados}</span>
              </p>
              <p className="text-slate-300">
                Gols sofridos: <span className="font-medium text-white">{estatisticas.gols_sofridos}</span>
              </p>
              <p className="text-slate-300 col-span-2 sm:col-span-3">
                Média de gols por jogo: <span className="font-medium text-white">{estatisticas.media_gols}</span>
              </p>
            </div>
          </div>
        )}

        <h2 className="mt-8 text-lg font-semibold">Últimos Jogos</h2>

        <ul className="mt-4 grid gap-2">
          {jogos.map((jogo, index) => (
            <li
              key={index}
              className={`rounded-md px-4 py-3 text-sm ${resultadoEstilo[jogo.resultado] ?? "border-l-4 border-slate-700 bg-slate-900"}`}
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
      </div>
    </main>
  );
}