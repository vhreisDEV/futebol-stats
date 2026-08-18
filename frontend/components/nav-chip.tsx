import Link from "next/link";
import type { LucideIcon } from "lucide-react";

export type CorNavChip = "gold" | "rose" | "orange" | "emerald" | "neutral";

const ESTILOS: Record<CorNavChip, string> = {
  gold: "border-primary/40 bg-primary/10 text-primary hover:bg-primary/20",
  rose: "border-rose-500/40 bg-rose-500/10 text-rose-400 hover:bg-rose-500/20",
  orange: "border-orange-500/40 bg-orange-500/10 text-orange-400 hover:bg-orange-500/20",
  emerald: "border-emerald-500/40 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20",
  neutral: "border-border bg-transparent text-muted-foreground hover:bg-muted hover:text-foreground",
};

export function NavChip({
  href,
  label,
  icon: Icon,
  cor,
}: {
  href: string;
  label: string;
  icon: LucideIcon;
  cor: CorNavChip;
}) {
  return (
    <Link
      href={href}
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-wide transition-colors ${ESTILOS[cor]}`}
    >
      <Icon className="size-3.5" />
      {label}
    </Link>
  );
}
