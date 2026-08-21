"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { VhSpinner } from "@/components/vh-spinner";
import { API_URL } from "@/lib/api";
import { formatarDataHora } from "@/lib/formatar-data";

interface PartidaDetalhe {
  id: number;
  data: string | null;
  hora: string | null;
  status: string;
  rodada: number | null;
  time_mandante_id: number;
  time_mandante: string;
  time_visitante_id: number;
  time_visitante: string;
  gols_mandante: number | null;
  gols_visitante: number | null;
  escanteios_mandante: number | null;
  escanteios_visitante: number | null;
  chutes_mandante: number | null;
  chutes_visitante: number | null;
  chutes_gol_mandante: number | null;
  chutes_gol_visitante: number | null;
  cartoes_amarelos_mandante: number | null;
  cartoes_amarelos_visitante: number | null;
  cartoes_vermelhos_mandante: number | null;
  cartoes_vermelhos_visitante: number | null;
}

const STATUS_LABEL: Record<string, string> = {
  adiada: "Adiada",
  agendada: "Ainda não realizada",
};

function LinhaEstatistica({
  label,
  mandante,
  visitante,
}: {
  label: string;
  mandante: number | null;
  visitante: number | null;
}) {
  const mandanteVence = mandante !== null && visitante !== null && mandante > visitante;
  const visitanteVence = mandante !== null && visitante !== null && visitante > mandante;

  return (
    <div className="grid grid-cols-3 items-center gap-2 py-1.5 text-sm">
      <span
        className={`font-mono tabular-nums ${mandanteVence ? "font-semibold text-primary" : "text-muted-foreground"}`}
      >
        {mandante ?? "—"}
      </span>
      <span className="text-center text-xs text-muted-foreground">{label}</span>
      <span
        className={`text-right font-mono tabular-nums ${visitanteVence ? "font-semibold text-primary" : "text-muted-foreground"}`}
      >
        {visitante ?? "—"}
      </span>
    </div>
  );
}

export function PartidaModal({
  partidaId,
  onClose,
}: {
  partidaId: number | null;
  onClose: () => void;
}) {
  const [partida, setPartida] = useState<PartidaDetalhe | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (partidaId === null) {
      setPartida(null);
      return;
    }

    setCarregando(true);
    setErro(null);

    fetch(`${API_URL}/partidas/${partidaId}`)
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar dados da partida");
        return r.json();
      })
      .then((dados: PartidaDetalhe) => {
        setPartida(dados);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, [partidaId]);

  return (
    <Dialog open={partidaId !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="sr-only">Detalhes da partida</DialogTitle>
          {carregando && (
            <div className="flex min-h-32 items-center justify-center py-2">
              <VhSpinner />
            </div>
          )}
          {erro && <p className="text-sm text-destructive">Erro: {erro}</p>}
          {partida && (
            <>
              <p className="text-center text-xs text-muted-foreground">
                {formatarDataHora(partida.data, partida.hora)}
                {partida.rodada !== null && ` · Rodada ${partida.rodada}`}
              </p>
              <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3">
                <Link
                  href={`/times/${partida.time_mandante_id}`}
                  className="truncate text-right font-heading text-sm uppercase tracking-wide transition-colors hover:text-primary"
                >
                  {partida.time_mandante}
                </Link>
                {partida.status === "finalizada" ? (
                  <span className="shrink-0 font-mono text-2xl font-bold tabular-nums text-primary">
                    {partida.gols_mandante}–{partida.gols_visitante}
                  </span>
                ) : (
                  <span
                    className={`shrink-0 text-xs font-bold uppercase tracking-wide ${partida.status === "adiada" ? "text-amber-400" : "text-muted-foreground"}`}
                  >
                    {STATUS_LABEL[partida.status] ?? partida.status}
                  </span>
                )}
                <Link
                  href={`/times/${partida.time_visitante_id}`}
                  className="truncate text-left font-heading text-sm uppercase tracking-wide transition-colors hover:text-primary"
                >
                  {partida.time_visitante}
                </Link>
              </div>
            </>
          )}
        </DialogHeader>

        {partida && partida.status === "finalizada" && (
          <div className="divide-y divide-border">
            <LinhaEstatistica
              label="Escanteios"
              mandante={partida.escanteios_mandante}
              visitante={partida.escanteios_visitante}
            />
            <LinhaEstatistica
              label="Chutes"
              mandante={partida.chutes_mandante}
              visitante={partida.chutes_visitante}
            />
            <LinhaEstatistica
              label="Chutes ao gol"
              mandante={partida.chutes_gol_mandante}
              visitante={partida.chutes_gol_visitante}
            />
            <LinhaEstatistica
              label="Cartões amarelos"
              mandante={partida.cartoes_amarelos_mandante}
              visitante={partida.cartoes_amarelos_visitante}
            />
            <LinhaEstatistica
              label="Cartões vermelhos"
              mandante={partida.cartoes_vermelhos_mandante}
              visitante={partida.cartoes_vermelhos_visitante}
            />
          </div>
        )}

        {partida && partida.status !== "finalizada" && (
          <p className="py-4 text-center text-sm text-muted-foreground">
            {partida.status === "adiada"
              ? "Essa partida foi adiada. Assim que for remarcada e jogada, o placar e as estatísticas aparecem aqui automaticamente."
              : "Essa partida ainda não foi realizada."}
          </p>
        )}
      </DialogContent>
    </Dialog>
  );
}
