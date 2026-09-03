"use client";

import { useEffect, useState } from "react";
import { API_URL, RODADA_MINIMA_FUNCOES_AVANCADAS } from "@/lib/api";
import { flagSrc } from "@/lib/paises";

interface Campeonato {
  id: number;
  nome: string;
  pais_codigo: string;
  temporada_label: string;
  rodada_atual: number | null;
}

/**
 * Dropdown de campeonato ativo, pra telas que ainda so tem uma unica
 * liga selecionada de cada vez (Comparar, Previsao, Dicas da Rodada,
 * Jogadores) -- nenhuma delas tem navegacao multi-campeonato de
 * verdade ainda, so um seletor simples que troca o campeonato_id usado
 * nas chamadas da propria tela.
 *
 * So lista ligas que ja passaram da RODADA_MINIMA_FUNCOES_AVANCADAS --
 * o campeonato selecionado no momento sempre aparece, mesmo que ainda
 * nao tenha cruzado a rodada minima (evita a liga escolhida sumir da
 * lista debaixo do usuario).
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
  const opcoes = campeonatos.filter(
    (c) => c.id === value || (c.rodada_atual ?? 0) >= RODADA_MINIMA_FUNCOES_AVANCADAS
  );

  if (opcoes.length <= 1) {
    return (
      <div className="inline-flex items-center gap-1.5 rounded-lg border border-input bg-card py-1.5 pr-3 pl-2.5 text-sm text-foreground">
        {atual && (
          // eslint-disable-next-line @next/next/no-img-element -- SVG local, decorativo
          <img src={flagSrc(atual.pais_codigo)} alt="" className="h-3 w-auto rounded-[1px]" />
        )}
        <span>{atual ? `${atual.nome} ${atual.temporada_label}` : "Brasileirão Série A 2026"}</span>
      </div>
    );
  }

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
        {opcoes.map((c) => (
          <option key={c.id} value={c.id}>
            {c.nome} {c.temporada_label}
          </option>
        ))}
      </select>
    </div>
  );
}
