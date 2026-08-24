/**
 * Emoji de bandeira por pais_codigo (ISO do Campeonato). Emoji em vez de
 * logo da liga/escudo -- evita qualquer questao de marca registrada,
 * renderiza nativo (sem asset pra hospedar) e escala com o tamanho da
 * fonte. GB-ENG (subdivisao, nao pais) usa a bandeira do Reino Unido
 * (🇬🇧), nao a sequencia "tag" da bandeira da Inglaterra (🏴󠁧󠁢󠁥󠁮󠁧󠁿) --
 * essa ultima tem suporte inconsistente mesmo em dispositivos reais
 * (alguns Android/apps renderizam so uma bandeira preta generica), a
 * de indicador regional simples (2 letras) e' bem mais confiavel.
 */
const BANDEIRAS: Record<string, string> = {
  BR: "🇧🇷",
  "GB-ENG": "🇬🇧",
  ES: "🇪🇸",
  DE: "🇩🇪",
  IT: "🇮🇹",
  FR: "🇫🇷",
};

export function bandeiraPais(paisCodigo: string): string {
  return BANDEIRAS[paisCodigo] ?? "🏳️";
}
