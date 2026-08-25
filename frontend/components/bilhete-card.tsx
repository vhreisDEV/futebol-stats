import { Trophy, Layers } from "lucide-react";
import type { Destaque } from "@/components/lista-destaques";
import { sumulaMono } from "@/lib/fonts";

export interface Perna {
  time: "mandante" | "visitante";
  nome_time: string;
  destaque: Destaque;
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
      {p.nome_time} ({mando}): mais de <span className={`${sumulaMono.className} font-bold text-primary`}>{d.linha}</span>{" "}
      {d.label.toLowerCase()}
    </>
  );
}

export interface CategoriaTotal {
  stat: string;
  nomeStat: string;
  principal: Perna;
  extras: Perna[];
}

// Os mercados de "total do jogo" vem um por time+mando (ex.: chutes
// olhando os jogos do Botafogo em casa E olhando os jogos do
// Athletico-PR fora, separadamente) -- listar os dois lado a lado como
// itens soltos obrigava o usuario a comparar e decidir sozinho qual
// numero valia mais. Agrupar por categoria (chutes/escanteios/cartoes) e
// escolher o palpite de maior taxa como "principal" da um numero so por
// categoria, mantendo o outro sinal visivel como apoio (nunca inventa
// media nem soma -- so escolhe qual dos dois sinais reais e' o mais
// forte).
export function agruparTotais(pernas: Perna[]): CategoriaTotal[] {
  const grupos = new Map<string, Perna[]>();
  for (const p of pernas) {
    const lista = grupos.get(p.destaque.stat) ?? [];
    lista.push(p);
    grupos.set(p.destaque.stat, lista);
  }

  return Array.from(grupos.values()).map((lista) => {
    // Maior taxa primeiro; empatado, prefere a linha mais alta (sinal
    // mais forte pra mesma confianca).
    const [principal, ...extras] = [...lista].sort(
      (a, b) => b.destaque.taxa - a.destaque.taxa || b.destaque.linha - a.destaque.linha
    );
    const nomeStat = principal.destaque.label.replace(/ totais no jogo/i, "");
    return { stat: principal.destaque.stat, nomeStat, principal, extras };
  });
}

export function CategoriaTotalCard({ categoria }: { categoria: CategoriaTotal }) {
  const { principal, extras, nomeStat } = categoria;
  const mando = principal.time === "mandante" ? "em casa" : "fora de casa";
  const porcentagem = Math.round(principal.destaque.taxa * 100);

  return (
    <li className="rounded-md bg-muted/40 p-2.5">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[10px] font-bold uppercase tracking-wide text-emerald-400">{nomeStat}</span>
        <span className="flex items-baseline gap-1 whitespace-nowrap">
          <span className={`${sumulaMono.className} text-base font-bold text-emerald-400`}>
            {principal.destaque.linha}+
          </span>
          <span className={`${sumulaMono.className} text-[10px] text-muted-foreground`}>{porcentagem}%</span>
        </span>
      </div>
      <p className="mt-0.5 text-[11px] text-muted-foreground">
        {principal.nome_time} {mando} (somando os dois times no jogo)
      </p>
      {extras.length > 0 && (
        <>
          <p className="mt-1 border-t border-emerald-500/10 pt-1 text-[10px] text-muted-foreground/70">
            Também vale considerar:{" "}
            {extras.map((e, i) => (
              <span key={i}>
                {i > 0 && " · "}
                {e.nome_time} {e.time === "mandante" ? "em casa" : "fora de casa"}: mais de{" "}
                <span className={sumulaMono.className}>{e.destaque.linha}</span> ({Math.round(e.destaque.taxa * 100)}%)
              </span>
            ))}
          </p>
          {/* Media combinada = media real de cada time (nao a "linha", que
              e' um piso conservador escolhido pra bater em 70-90% dos
              jogos, sempre mais baixo que a media de verdade) -- os dois
              numeros de `media` ja vem calculados pelo backend a partir do
              historico real, so' juntamos os dois aqui. */}
          <p className="mt-1 text-[10px] text-muted-foreground/70">
            Média combinada esperada:{" "}
            <span className={`${sumulaMono.className} font-semibold text-emerald-400`}>
              ~{Math.round(((principal.destaque.media + extras[0].destaque.media) / 2) * 10) / 10}
            </span>
          </p>
        </>
      )}
    </li>
  );
}

// O Bilhete Simples e' o "veredito" da pagina -- card maior e mais
// chamativo que o resto, pra quem quer decidir rapido bater o olho e ja
// saber qual e' o palpite principal, sem precisar comparar cards do
// mesmo tamanho pra descobrir qual e' o mais importante.
export function BilheteSimplesCard({ perna }: { perna: Perna }) {
  const porcentagem = Math.round(perna.destaque.taxa * 100);
  return (
    <div className="rounded-md border-2 border-primary/40 bg-gradient-to-br from-primary/10 via-card to-card p-4">
      <div className="flex items-center gap-1.5">
        <Trophy className="size-4 text-primary" />
        <span className="text-[11px] font-bold uppercase tracking-wide text-primary">Bilhete Simples</span>
      </div>
      <p className="text-base font-semibold leading-snug text-foreground sm:text-lg">{fraseCurta(perna)}</p>
      <div className="mt-1 flex items-baseline gap-1.5">
        <span className={`${sumulaMono.className} text-base font-bold tabular-nums text-primary`}>{porcentagem}%</span>
        <span className="text-xs text-muted-foreground">dos últimos {perna.destaque.total} jogos</span>
      </div>
    </div>
  );
}

export function BilheteMultiplaCard({ pernas }: { pernas: Perna[] }) {
  return (
    <div className="rounded-md border border-amber-500/30 bg-amber-500/5 p-3">
      <div className="flex items-center gap-1.5">
        <Layers className="size-3.5 text-amber-400" />
        <span className="text-[10px] font-bold uppercase tracking-wide text-amber-400">
          Bilhete múltipla · {pernas.length} seleções
        </span>
      </div>
      <ol className="mt-1.5 grid gap-1">
        {pernas.map((p, i) => (
          <li key={i} className="flex items-baseline gap-1.5 text-sm">
            <span className={`${sumulaMono.className} text-xs text-muted-foreground`}>{i + 1}.</span>
            <span className="min-w-0 flex-1 text-foreground">{fraseCurta(p)}</span>
            <span className={`${sumulaMono.className} shrink-0 text-xs font-semibold text-primary`}>
              {Math.round(p.destaque.taxa * 100)}%
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
