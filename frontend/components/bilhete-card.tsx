import { Ticket, Layers } from "lucide-react";
import type { Destaque } from "@/components/lista-destaques";

export interface Perna {
  time: "mandante" | "visitante";
  nome_time: string;
  destaque: Destaque;
}

export function SeloPRO() {
  return (
    <span className="ml-auto shrink-0 rounded-full bg-violet-500/20 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wide text-violet-300">
      PRO
    </span>
  );
}

export function fraseCurta(p: Perna) {
  const mando = p.time === "mandante" ? "em casa" : "fora de casa";
  const d = p.destaque;
  if (d.tipo === "booleano") {
    return (
      <>
        {p.nome_time} ({mando}): {d.label.toLowerCase()}
      </>
    );
  }
  return (
    <>
      {p.nome_time} ({mando}): mais de <span className="font-mono font-bold text-primary">{d.linha}</span>{" "}
      {d.label.toLowerCase()}
    </>
  );
}

// Mercados de "totais do jogo" somam os dois times -- "Athletico-PR
// (fora): mais de 18.5 chutes" lia como se fosse so o time dele, entao
// aqui a frase deixa explicito que e' a partida inteira, nao um lado so.
export function fraseTotal(p: Perna) {
  const mando = p.time === "mandante" ? "em casa" : "fora de casa";
  const d = p.destaque;
  const stat = d.label.replace(/ totais no jogo/i, "").toLowerCase();
  return (
    <>
      Jogos com {p.nome_time} {mando} costumam ter mais de{" "}
      <span className="font-mono font-bold text-primary">{d.linha}</span> {stat} no total (somando os dois
      times)
    </>
  );
}

export function BilheteSimplesCard({ perna }: { perna: Perna }) {
  return (
    <div className="rounded-lg border border-violet-500/30 bg-violet-500/5 p-3">
      <div className="flex items-center gap-1.5">
        <Ticket className="size-3.5 text-violet-400" />
        <span className="text-[10px] font-bold uppercase tracking-wide text-violet-400">Bilhete simples</span>
        <SeloPRO />
      </div>
      <p className="mt-1.5 text-sm font-medium text-foreground">{fraseCurta(perna)}</p>
      <p className="text-xs text-muted-foreground">
        <span className="font-mono font-semibold text-primary">{Math.round(perna.destaque.taxa * 100)}%</span> dos
        últimos {perna.destaque.total} jogos
      </p>
    </div>
  );
}

export function BilheteMultiplaCard({ pernas }: { pernas: Perna[] }) {
  return (
    <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3">
      <div className="flex items-center gap-1.5">
        <Layers className="size-3.5 text-amber-400" />
        <span className="text-[10px] font-bold uppercase tracking-wide text-amber-400">
          Bilhete múltipla · {pernas.length} seleções
        </span>
        <SeloPRO />
      </div>
      <ol className="mt-1.5 grid gap-1">
        {pernas.map((p, i) => (
          <li key={i} className="flex items-baseline gap-1.5 text-sm">
            <span className="font-mono text-xs text-muted-foreground">{i + 1}.</span>
            <span className="min-w-0 flex-1 text-foreground">{fraseCurta(p)}</span>
            <span className="shrink-0 font-mono text-xs font-semibold text-primary">
              {Math.round(p.destaque.taxa * 100)}%
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
