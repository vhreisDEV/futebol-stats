"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";

interface LinhaClassificacao {
  posicao: number;
  time_id: number;
  time: string;
  pontos: number;
  jogos: number;
  vitorias: number;
  empates: number;
  derrotas: number;
  gols_pro: number;
  gols_contra: number;
  saldo_gols: number;
}

interface ClassificacaoResponse {
  classificacao: LinhaClassificacao[];
}

interface Zona {
  min: number;
  max: number;
  label: string;
  corBorda: string;
  corLegenda: string;
}

// Faixas de classificacao do Brasileirao Serie A (regulamento CBF).
const ZONAS: Zona[] = [
  { min: 1, max: 4, label: "Libertadores", corBorda: "border-l-blue-500", corLegenda: "bg-blue-500" },
  { min: 5, max: 6, label: "Pré-Libertadores", corBorda: "border-l-green-500", corLegenda: "bg-green-500" },
  { min: 7, max: 12, label: "Sul-Americana", corBorda: "border-l-cyan-500", corLegenda: "bg-cyan-500" },
  { min: 17, max: 20, label: "Rebaixamento", corBorda: "border-l-red-500", corLegenda: "bg-red-500" },
];

function zonaDaPosicao(posicao: number) {
  return ZONAS.find((z) => posicao >= z.min && posicao <= z.max) ?? null;
}

export function Classificacao({ ateRodada }: { ateRodada: number | null }) {
  const [tabela, setTabela] = useState<LinhaClassificacao[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (ateRodada === null) return;

    setCarregando(true);

    fetch(`http://127.0.0.1:8000/classificacao/?ate_rodada=${ateRodada}`)
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar classificação");
        return r.json();
      })
      .then((dados: ClassificacaoResponse) => {
        setTabela(dados.classificacao);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, [ateRodada]);

  if (erro) {
    return <p className="text-sm text-destructive">Erro: {erro}</p>;
  }

  if (carregando) {
    return (
      <div className="grid gap-1.5">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-8 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="text-center">#</TableHead>
            <TableHead>Time</TableHead>
            <TableHead className="text-center">P</TableHead>
            <TableHead className="text-center">J</TableHead>
            <TableHead className="text-center">V</TableHead>
            <TableHead className="text-center">E</TableHead>
            <TableHead className="text-center">D</TableHead>
            <TableHead className="text-center">GP</TableHead>
            <TableHead className="text-center">GC</TableHead>
            <TableHead className="text-center">SG</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tabela.map((linha) => {
            const zona = zonaDaPosicao(linha.posicao);
            return (
              <TableRow
                key={linha.time_id}
                className={`border-l-4 ${zona?.corBorda ?? "border-l-transparent"}`}
              >
                <TableCell className="text-center font-mono tabular-nums text-muted-foreground">
                  {linha.posicao}
                </TableCell>
                <TableCell>
                  <Link
                    href={`/times/${linha.time_id}`}
                    className="font-medium transition-colors hover:text-primary"
                  >
                    {linha.time}
                  </Link>
                </TableCell>
                <TableCell className="text-center font-mono font-semibold tabular-nums text-primary">
                  {linha.pontos}
                </TableCell>
                <TableCell className="text-center font-mono tabular-nums text-muted-foreground">
                  {linha.jogos}
                </TableCell>
                <TableCell className="text-center font-mono tabular-nums text-muted-foreground">
                  {linha.vitorias}
                </TableCell>
                <TableCell className="text-center font-mono tabular-nums text-muted-foreground">
                  {linha.empates}
                </TableCell>
                <TableCell className="text-center font-mono tabular-nums text-muted-foreground">
                  {linha.derrotas}
                </TableCell>
                <TableCell className="text-center font-mono tabular-nums text-muted-foreground">
                  {linha.gols_pro}
                </TableCell>
                <TableCell className="text-center font-mono tabular-nums text-muted-foreground">
                  {linha.gols_contra}
                </TableCell>
                <TableCell className="text-center font-mono tabular-nums text-muted-foreground">
                  {linha.saldo_gols}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5">
        {ZONAS.map((zona) => (
          <div key={zona.label} className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <span className={`size-2.5 rounded-sm ${zona.corLegenda}`} />
            {zona.label}
          </div>
        ))}
      </div>
    </div>
  );
}
