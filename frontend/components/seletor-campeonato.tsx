"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";
import { flagSrc } from "@/lib/paises";

interface Campeonato {
  id: number;
  nome: string;
  pais_codigo: string;
  temporada_label: string;
}

/**
 * Dropdown de campeonato ativo, pra telas que ainda so tem uma unica
 * liga selecionada de cada vez (Comparar, Previsao, Dicas da Rodada,
 * Jogadores) -- nenhuma delas tem navegacao multi-campeonato de
 * verdade ainda, so um seletor simples que troca o campeonato_id usado
 * nas chamadas da propria tela.
 */
export function SeletorCampeonato({
  value,
  onChange,
}: {
  value: number;
  onChange: (campeonatoId: number) => void;
}) {
  const [campeonatos, setCampeonatos] = useState<Campeonato[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/campeonatos/`)
      .then((r) => (r.ok ? r.json() : { campeonatos: [] }))
      .then((dados: { campeonatos: Campeonato[] }) => setCampeonatos(dados.campeonatos))
      .catch(() => {});
  }, []);

  const atual = campeonatos.find((c) => c.id === value);

  return (
    <div className="relative inline-flex items-center">
      {atual && (
        // eslint-disable-next-line @next/next/no-img-element -- SVG local, decorativo
        <img
          src={flagSrc(atual.pais_codigo)}
          alt=""
          className="pointer-events-none absolute left-2.5 h-3 w-auto rounded-[1px]"
        />
      )}
      <select
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className={`rounded-lg border border-input bg-card py-1.5 pr-3 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 ${atual ? "pl-8" : "pl-3"}`}
      >
        {campeonatos.map((c) => (
          <option key={c.id} value={c.id}>
            {c.nome} {c.temporada_label}
          </option>
        ))}
      </select>
    </div>
  );
}
