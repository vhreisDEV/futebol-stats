/**
 * Emoji de bandeira por pais_codigo (ISO do Campeonato). Emoji em vez de
 * logo da liga/escudo -- evita qualquer questao de marca registrada,
 * renderiza nativo (sem asset pra hospedar) e escala com o tamanho da
 * fonte. GB-ENG (subdivisao, nao pais) usa a sequencia Unicode da
 * bandeira da Inglaterra (tag sequence), nao a UK -- suportada nos
 * navegadores/SOs modernos.
 */
const BANDEIRAS: Record<string, string> = {
  BR: "🇧🇷",
  "GB-ENG": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
  ES: "🇪🇸",
  DE: "🇩🇪",
  IT: "🇮🇹",
  FR: "🇫🇷",
};

export function bandeiraPais(paisCodigo: string): string {
  return BANDEIRAS[paisCodigo] ?? "🏳️";
}
