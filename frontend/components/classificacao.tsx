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
        {tabela.map((linha) => (
          <TableRow key={linha.time_id}>
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
        ))}
      </TableBody>
    </Table>
  );
}
