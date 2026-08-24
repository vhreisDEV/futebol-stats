const CORES_NOTA = {
  alta: "text-emerald-400",
  media: "text-primary",
  baixa: "text-muted-foreground",
};

function corPorNota(nota: number) {
  if (nota >= 7) return CORES_NOTA.alta;
  if (nota >= 4) return CORES_NOTA.media;
  return CORES_NOTA.baixa;
}

export function NotaPartida({ label, nota }: { label: string; nota: number | null }) {
  if (nota === null) {
    return (
      <div>
        <p className="text-[10px] uppercase tracking-wide text-muted-foreground/70">{label}</p>
        <p className="mt-0.5 text-xs text-muted-foreground/50">sem dado</p>
      </div>
    );
  }

  const cor = corPorNota(nota);

  return (
    <div>
      <div className="flex items-baseline justify-between gap-2">
        <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
        <p className={`font-mono text-xs font-bold tabular-nums ${cor}`}>
          {nota.toFixed(1)}
          <span className="text-muted-foreground/60">/10</span>
        </p>
      </div>
      <div className="mt-1 h-1 w-full overflow-hidden rounded-full bg-background/60">
        <div className={`h-full rounded-full bg-current ${cor}`} style={{ width: `${nota * 10}%` }} />
      </div>
    </div>
  );
}
