"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Crown } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { API_URL } from "@/lib/api";

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
// Cores escolhidas para ficarem bem distintas entre si (evitar tons
// de azul proximos um do outro).
const ZONAS: Zona[] = [
  { min: 1, max: 4, label: "Libertadores", corBorda: "!border-l-blue-500", corLegenda: "bg-blue-500" },
  { min: 5, max: 6, label: "Pré-Libertadores", corBorda: "!border-l-green-500", corLegenda: "bg-green-500" },
  { min: 7, max: 12, label: "Sul-Americana", corBorda: "!border-l-violet-500", corLegenda: "bg-violet-500" },
  { min: 17, max: 20, label: "Rebaixamento", corBorda: "!border-l-red-500", corLegenda: "bg-red-500" },
];

function zonaDaPosicao(posicao: number) {
  return ZONAS.find((z) => posicao >= z.min && posicao <= z.max) ?? null;
}

export function Classificacao() {
  const [tabela, setTabela] = useState<LinhaClassificacao[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  // A classificacao mostra sempre a posicao atual (todos os jogos ja
  // importados), independente da rodada navegada ao lado -- o Brasileirao
  // tem jogos atrasados, entao "classificacao ate a rodada X" nao bate
  // com a tabela real numa boa parte do campeonato.
  useEffect(() => {
    fetch(`${API_URL}/classificacao/`)
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
  }, []);

  if (erro) {
    return <p className="text-sm text-destructive">Erro: {erro}</p>;
  }

  if (carregando) {
    return (
      <div className="grid gap-1">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-6 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow className="!border-b-2 !border-b-primary/30">
            <TableHead className="h-7 px-1.5 text-center text-[11px] uppercase tracking-wide text-primary/80">#</TableHead>
            <TableHead className="h-7 px-1.5 text-[11px] uppercase tracking-wide text-primary/80">Time</TableHead>
            <TableHead className="h-7 px-1.5 text-center text-[11px] uppercase tracking-wide text-primary/80">P</TableHead>
            <TableHead className="h-7 px-1.5 text-center text-[11px] uppercase tracking-wide text-primary/80">J</TableHead>
            <TableHead className="h-7 px-1.5 text-center text-[11px] uppercase tracking-wide text-primary/80">V</TableHead>
            <TableHead className="h-7 px-1.5 text-center text-[11px] uppercase tracking-wide text-primary/80">E</TableHead>
            <TableHead className="h-7 px-1.5 text-center text-[11px] uppercase tracking-wide text-primary/80">D</TableHead>
            <TableHead className="h-7 px-1.5 text-center text-[11px] uppercase tracking-wide text-primary/80">GP</TableHead>
            <TableHead className="h-7 px-1.5 text-center text-[11px] uppercase tracking-wide text-primary/80">GC</TableHead>
            <TableHead className="h-7 px-1.5 text-center text-[11px] uppercase tracking-wide text-primary/80">SG</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tabela.map((linha) => {
            const zona = zonaDaPosicao(linha.posicao);
            const lider = linha.posicao === 1;
            return (
              <TableRow
                key={linha.time_id}
                className={`!border-l-4 text-xs ${zona?.corBorda ?? "!border-l-transparent"} ${lider ? "!bg-primary/[0.06]" : ""}`}
              >
                <TableCell className="px-1.5 py-1 text-center font-mono tabular-nums text-muted-foreground">
                  {linha.posicao}
                </TableCell>
                <TableCell className="px-1.5 py-1">
                  <Link
                    href={`/times/${linha.time_id}`}
                    className="flex items-center gap-1 font-medium transition-colors hover:text-primary"
                  >
                    {lider && <Crown className="size-3 shrink-0 text-primary" strokeWidth={2.5} />}
                    {linha.time}
                  </Link>
                </TableCell>
                <TableCell className="px-1.5 py-1 text-center font-mono font-semibold tabular-nums text-primary">
                  {linha.pontos}
                </TableCell>
                <TableCell className="px-1.5 py-1 text-center font-mono tabular-nums text-muted-foreground">
                  {linha.jogos}
                </TableCell>
                <TableCell className="px-1.5 py-1 text-center font-mono tabular-nums text-muted-foreground">
                  {linha.vitorias}
                </TableCell>
                <TableCell className="px-1.5 py-1 text-center font-mono tabular-nums text-muted-foreground">
                  {linha.empates}
                </TableCell>
                <TableCell className="px-1.5 py-1 text-center font-mono tabular-nums text-muted-foreground">
                  {linha.derrotas}
                </TableCell>
                <TableCell className="px-1.5 py-1 text-center font-mono tabular-nums text-muted-foreground">
                  {linha.gols_pro}
                </TableCell>
                <TableCell className="px-1.5 py-1 text-center font-mono tabular-nums text-muted-foreground">
                  {linha.gols_contra}
                </TableCell>
                <TableCell className="px-1.5 py-1 text-center font-mono tabular-nums text-muted-foreground">
                  {linha.saldo_gols}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1">
        {ZONAS.map((zona) => (
          <div key={zona.label} className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <span className={`size-2 rounded-sm ${zona.corLegenda}`} />
            {zona.label}
          </div>
        ))}
      </div>
    </div>
  );
}
