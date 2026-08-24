/**
 * Codigo de bandeira por pais_codigo do Campeonato -- usado pra montar o
 * caminho do SVG estatico em public/flags/. SVG de bandeira nacional em
 * vez de emoji: emoji de bandeira depende de fonte com a ligatura certa,
 * e o Windows historicamente so mostra as iniciais do pais numa
 * etiqueta em vez da bandeira de verdade (confirmado em producao, nao
 * renderiza mesmo forcando a fonte via CSS). SVG tambem nao tem risco
 * de marca registrada (bandeira nacional e simbolo publico, diferente
 * de escudo/logo de time ou liga). GB-ENG usa a bandeira de Sao Jorge
 * (gb-eng), a bandeira regional da Inglaterra -- o flag-icons tambem
 * tem as das outras subdivisoes do Reino Unido (gb-sct, gb-wls, gb-nir)
 * se algum campeonato de la for adicionado no futuro.
 *
 * Os SVGs vem do pacote flag-icons (MIT, github.com/lipis/flag-icons),
 * copiados direto pra public/flags/ em vez de importados via npm -- ver
 * public/flags/NOTICE.md pra detalhes de por que.
 */
const CODIGOS_FLAG: Record<string, string> = {
  BR: "br",
  "GB-ENG": "gb-eng",
  ES: "es",
  DE: "de",
  IT: "it",
  FR: "fr",
};

function codigoFlag(paisCodigo: string): string {
  return CODIGOS_FLAG[paisCodigo] ?? "xx";
}

/** Caminho do SVG retangular (4x3), pra usar ao lado de titulo/texto. */
export function flagSrc(paisCodigo: string): string {
  return `/flags/4x3/${codigoFlag(paisCodigo)}.svg`;
}

/** Caminho do SVG quadrado (1x1), pra usar em badges circulares. */
export function flagSrcQuadrada(paisCodigo: string): string {
  return `/flags/1x1/${codigoFlag(paisCodigo)}.svg`;
}
