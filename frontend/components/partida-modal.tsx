"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Space_Mono } from "next/font/google";
import { Sparkles } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { VhSpinner } from "@/components/vh-spinner";
import { API_URL } from "@/lib/api";
import { formatarDataHora } from "@/lib/formatar-data";

// Fonte so' deste componente (prototipo da linha visual "sumula oficial"
// -- ver [[project_veaga_sumula_visual]]): Geist Mono e' a mono padrao de
// qualquer projeto Next.js, Space Mono tem mais cara de maquina de
// escrever/formulario carbonado, o que combina mais com "documento
// oficial preenchido a mao" do que com "interface de app".
const sumulaMono = Space_Mono({ subsets: ["latin"], weight: ["400", "700"] });

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
    <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 py-2">
      <span
        className={`${sumulaMono.className} text-right text-base tabular-nums ${mandanteVence ? "font-bold text-primary" : "text-muted-foreground"}`}
      >
        {mandante ?? "—"}
      </span>
      <span className="text-center text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">
        {label}
      </span>
      <span
        className={`${sumulaMono.className} text-left text-base tabular-nums ${visitanteVence ? "font-bold text-primary" : "text-muted-foreground"}`}
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
      <DialogContent className="gap-0 overflow-hidden rounded-md p-0 ring-1 ring-primary/25 sm:max-w-md">
        <DialogHeader className="gap-0">
          <DialogTitle className="sr-only">Súmula da partida</DialogTitle>

          {/* Cabecalho tipo formulario oficial -- numero do documento e'
              o id real da partida (dado de verdade, nao decoracao). */}
          <div className="flex items-center justify-between border-b border-primary/25 px-4 py-2.5">
            <span className="font-heading text-[10px] font-semibold uppercase tracking-[0.25em] text-muted-foreground">
              VEAGA · Súmula
            </span>
            {partida && (
              <span className={`${sumulaMono.className} text-[10px] tracking-wide text-primary/80`}>
                Nº {String(partida.id).padStart(6, "0")}
              </span>
            )}
          </div>

          {carregando && (
            <div className="flex min-h-32 items-center justify-center py-2">
              <VhSpinner />
            </div>
          )}
          {erro && <p className="px-4 py-4 text-sm text-destructive">Erro: {erro}</p>}

          {partida && (
            <div className="px-4 pt-3">
              <p className="text-center text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                {formatarDataHora(partida.data, partida.hora)}
                {partida.rodada !== null && ` · Rodada ${partida.rodada}`}
              </p>
              <div className="mt-2 grid grid-cols-[1fr_auto_1fr] items-center gap-3 border-y border-primary/15 py-3">
                <Link
                  href={`/times/${partida.time_mandante_id}`}
                  className="truncate text-right font-heading text-sm uppercase tracking-wide transition-colors hover:text-primary"
                >
                  {partida.time_mandante}
                </Link>
                {partida.status === "finalizada" ? (
                  <span className={`${sumulaMono.className} shrink-0 text-2xl font-bold tabular-nums text-primary`}>
                    {partida.gols_mandante}–{partida.gols_visitante}
                  </span>
                ) : (
                  <span
                    className={`shrink-0 text-[10px] font-bold uppercase tracking-wide ${partida.status === "adiada" ? "text-amber-400" : "text-muted-foreground"}`}
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
            </div>
          )}
        </DialogHeader>

        {partida && partida.status === "finalizada" && (
          <div className="relative px-4 pb-4">
            <div className="divide-y divide-primary/10">
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

            {/* "Carimbo" -- unico floreio decorativo do card, so' aparece
                em jogo ja apurado (a sumula so' e' "conferida" depois do
                jogo acontecer). Girado, meio transparente, como um
                carimbo de verdade batido meio torto. */}
            <div
              aria-hidden
              className="animate-in zoom-in-50 fade-in pointer-events-none absolute -right-1 bottom-1 flex size-16 rotate-[-12deg] items-center justify-center rounded-full border-2 border-primary/40 text-center duration-500 motion-reduce:animate-none"
            >
              <span className="font-heading text-[9px] font-bold leading-tight tracking-[0.1em] text-primary/50">
                CONFE
                <br />
                RIDO
              </span>
            </div>
          </div>
        )}

        {partida && partida.status !== "finalizada" && (
          <p className="px-4 py-4 text-center text-sm text-muted-foreground">
            {partida.status === "adiada"
              ? "Essa partida foi adiada. Assim que for remarcada e jogada, o placar e as estatísticas aparecem aqui automaticamente."
              : "Essa partida ainda não foi realizada."}
          </p>
        )}

        {partida && partida.status === "agendada" && (
          <div className="px-4 pb-4">
            <Link
              href={`/analise/${partida.id}`}
              className="flex items-center justify-center gap-1.5 rounded-lg border border-primary/30 bg-primary/5 py-2.5 text-sm font-medium text-primary transition-colors hover:bg-primary/10"
            >
              <Sparkles className="size-4" />
              Análise da IA
            </Link>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
