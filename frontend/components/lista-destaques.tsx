import {
  Flag,
  Target,
  Crosshair,
  RectangleVertical,
  CircleDot,
  ArrowLeftRight,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";

export interface Destaque {
  stat: string;
  label: string;
  tipo: "quantidade" | "booleano";
  linha: number;
  acertos: number;
  total: number;
  taxa: number;
  sequencia: number[];
  media: number;
}

export const ICONE_STAT: Record<string, { icon: LucideIcon; cor: string }> = {
  gols_marcados: { icon: CircleDot, cor: "text-emerald-400" },
  escanteios_a_favor: { icon: Flag, cor: "text-blue-400" },
  chutes_a_favor: { icon: Target, cor: "text-violet-400" },
  chutes_gol_a_favor: { icon: Crosshair, cor: "text-rose-400" },
  cartoes_amarelos: { icon: RectangleVertical, cor: "text-amber-400" },
  ambas_marcam: { icon: ArrowLeftRight, cor: "text-cyan-400" },
  sem_perder: { icon: ShieldCheck, cor: "text-lime-400" },
};

export function fraseDestaque(time: string, mandoLabel: "em casa" | "fora de casa", d: Destaque) {
  const porcentagem = Math.round(d.taxa * 100);

  if (d.stat === "ambas_marcam") {
    return (
      <>
        Nos jogos de <span className="font-semibold">{time}</span> {mandoLabel}, ambas equipes costumam marcar —{" "}
        <span className="font-mono font-semibold">
          {d.acertos}/{d.total}
        </span>{" "}
        jogos ({porcentagem}%)
      </>
    );
  }
  if (d.stat === "sem_perder") {
    return (
      <>
        <span className="font-semibold">{time}</span> costuma não perder {mandoLabel} —{" "}
        <span className="font-mono font-semibold">
          {d.acertos}/{d.total}
        </span>{" "}
        jogos ({porcentagem}%)
      </>
    );
  }
  return (
    <>
      <span className="font-semibold">{time}</span> costuma passar de{" "}
      <span className="font-mono font-semibold text-primary">{d.linha}</span> {d.label.toLowerCase()} {mandoLabel} —{" "}
      <span className="font-mono font-semibold">
        {d.acertos}/{d.total}
      </span>{" "}
      jogos ({porcentagem}%)
    </>
  );
}

export function SequenciaBadges({ destaque }: { destaque: Destaque }) {
  return (
    <p className="flex flex-wrap gap-1">
      {destaque.sequencia
        .slice()
        .reverse()
        .map((v, i) => (
          <span
            key={i}
            className={`rounded px-1.5 py-0.5 font-mono text-[10px] tabular-nums ${
              v > destaque.linha ? "bg-primary/15 font-semibold text-primary" : "bg-background/60 text-muted-foreground/70"
            }`}
          >
            {destaque.tipo === "booleano" ? (v > destaque.linha ? "✓" : "✗") : v}
          </span>
        ))}
    </p>
  );
}

export function ListaDestaques({
  time,
  mandoLabel,
  destaques,
  mostrarSequencia = false,
}: {
  time: string;
  mandoLabel: "em casa" | "fora de casa";
  destaques: Destaque[];
  mostrarSequencia?: boolean;
}) {
  if (destaques.length === 0) {
    return <p className="text-xs text-muted-foreground/70">Nada que se destaque {mandoLabel}.</p>;
  }

  return (
    <ul className="grid gap-2">
      {destaques.map((d) => {
        const { icon: Icon, cor } = ICONE_STAT[d.stat] ?? { icon: Flag, cor: "text-muted-foreground" };
        const porcentagem = Math.round(d.taxa * 100);

        return (
          <li key={d.stat} className="rounded-md bg-muted/40 p-2.5">
            <div className="flex items-start gap-2">
              <Icon className={`mt-0.5 size-3.5 shrink-0 ${cor}`} />
              <p className="text-xs leading-relaxed text-foreground">{fraseDestaque(time, mandoLabel, d)}</p>
            </div>
            <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-background/60">
              <div className={`h-full rounded-full bg-current ${cor}`} style={{ width: `${porcentagem}%` }} />
            </div>
            {mostrarSequencia && (
              <div className="mt-1.5 pl-5.5">
                <SequenciaBadges destaque={d} />
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
