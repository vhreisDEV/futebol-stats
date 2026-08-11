"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

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
          throw new Error("Erro ao buscar os jogos");
        }
        return r.json();
      }),

      fetch(`http://127.0.0.1:8000/times/${id}/estatisticas`).then((r) => {
        if (!r.ok) {
          throw new Error("Erro ao buscar as estatísticas");
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
    return <p>Carregando...</p>;
  }

  if (erro) {
    return <p>Erro: {erro}</p>;
  }

  return (
    <div>
      {estatisticas && (
        <div>
          <h2>Estatísticas</h2>

          <p>Total de jogos: {estatisticas.total_jogos}</p>
          <p>Vitórias: {estatisticas.vitorias}</p>
          <p>Empates: {estatisticas.empates}</p>
          <p>Derrotas: {estatisticas.derrotas}</p>
          <p>Gols marcados: {estatisticas.gols_marcados}</p>
          <p>Gols sofridos: {estatisticas.gols_sofridos}</p>
          <p>Média de gols: {estatisticas.media_gols}</p>
        </div>
      )}

      <h2>Jogos</h2>

      <ul>
        {jogos.map((jogo, index) => {
          const cor =
            jogo.resultado === "vitoria"
              ? "green"
              : jogo.resultado === "empate"
                ? "orange"
                : "red";

          return (
            <li key={index} style={{ color: cor }}>
              {jogo.data} -{" "}
              {jogo.casa_ou_fora === "casa" ? "vs" : "@"}{" "}
              {jogo.adversario} - {jogo.gols_time}x
              {jogo.gols_adversario} ({jogo.resultado})
            </li>
          );
        })}
      </ul>
    </div>
  );
}