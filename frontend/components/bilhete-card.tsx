import { Ticket, Layers } from "lucide-react";
import type { Destaque } from "@/components/lista-destaques";

export interface Perna {
  time: "mandante" | "visitante";
  nome_time: string;
  destaque: Destaque;
}

export function fraseCurta(p: Perna) {
  const mando = p.time === "mandante" ? "em casa" : "fora";
  const d = p.destaque;
  if (d.tipo === "booleano") {
    return `${p.nome_time} (${mando}): ${d.label.toLowerCase()}`;
  }
  return `${p.nome_time} (${mando}): mais de ${d.linha} ${d.label.toLowerCase()}`;
}

export function BilheteSimplesCard({ perna, confianca }: { perna: Perna; confianca: number }) {
  return (
    <div className="rounded-lg border border-violet-500/30 bg-violet-500/5 p-3">
      <div className="flex items-center gap-1.5">
        <Ticket className="size-3.5 text-violet-400" />
        <span className="text-[10px] font-bold uppercase tracking-wide text-violet-400">Bilhete simples</span>
        <span className="ml-auto rounded-full bg-violet-500/20 px-2 py-0.5 font-mono text-[10px] font-bold text-violet-300">
          {confianca.toFixed(1)}/10
        </span>
      </div>
      <p className="mt-1.5 text-sm font-medium text-foreground">{fraseCurta(perna)}</p>
      <p className="text-xs text-muted-foreground">
        {Math.round(perna.destaque.taxa * 100)}% dos últimos {perna.destaque.total} jogos
      </p>
    </div>
  );
}

export function BilheteMultiplaCard({
  pernas,
  confiancaCombinada,
}: {
  pernas: Perna[];
  confiancaCombinada: number;
}) {
  return (
    <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3">
      <div className="flex items-center gap-1.5">
        <Layers className="size-3.5 text-amber-400" />
        <span className="text-[10px] font-bold uppercase tracking-wide text-amber-400">
          Bilhete múltipla · {pernas.length} pernas
        </span>
        <span className="ml-auto rounded-full bg-amber-500/20 px-2 py-0.5 font-mono text-[10px] font-bold text-amber-300">
          {confiancaCombinada.toFixed(1)}/10
        </span>
      </div>
      <ol className="mt-1.5 grid gap-1">
        {pernas.map((p, i) => (
          <li key={i} className="flex items-baseline gap-1.5 text-sm">
            <span className="font-mono text-xs text-muted-foreground">{i + 1}.</span>
            <span className="min-w-0 flex-1 text-foreground">{fraseCurta(p)}</span>
            <span className="shrink-0 font-mono text-xs text-muted-foreground">
              {Math.round(p.destaque.taxa * 100)}%
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
