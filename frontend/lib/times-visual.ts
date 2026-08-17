// Cores reais das camisas/escudos de cada time (aproximadas) -- usadas
// como identidade visual provisoria ate termos os escudos de verdade.
export const CORES_TIME: Record<string, { fundo: string; borda: string; textoEscuro?: boolean }> = {
  "Athletico-PR": { fundo: "#C8102E", borda: "#000000" },
  "Atlético-MG": { fundo: "#000000", borda: "#FFFFFF" },
  Bahia: { fundo: "#0038A8", borda: "#E4022C" },
  Botafogo: { fundo: "#000000", borda: "#FFFFFF" },
  Chapecoense: { fundo: "#1B7B3A", borda: "#FFFFFF" },
  Corinthians: { fundo: "#000000", borda: "#FFFFFF" },
  Coritiba: { fundo: "#0F7A3D", borda: "#FFFFFF" },
  Cruzeiro: { fundo: "#003DA5", borda: "#FFFFFF" },
  Flamengo: { fundo: "#C8102E", borda: "#000000" },
  Fluminense: { fundo: "#8B1538", borda: "#046A38" },
  Grêmio: { fundo: "#0D80C7", borda: "#000000" },
  Internacional: { fundo: "#E2001A", borda: "#FFFFFF" },
  Mirassol: { fundo: "#FFD400", borda: "#1B7B3A", textoEscuro: true },
  Palmeiras: { fundo: "#006437", borda: "#FFFFFF" },
  "Red Bull Bragantino": { fundo: "#D50032", borda: "#FFFFFF" },
  Remo: { fundo: "#0033A0", borda: "#FFFFFF" },
  Santos: { fundo: "#FFFFFF", borda: "#000000", textoEscuro: true },
  "São Paulo": { fundo: "#C1121C", borda: "#000000" },
  "Vasco da Gama": { fundo: "#000000", borda: "#FFFFFF" },
  Vitória: { fundo: "#C8102E", borda: "#000000" },
};

export function corTime(nome: string) {
  return CORES_TIME[nome] ?? { fundo: "#3f3f46", borda: "#71717a" };
}

export function iniciais(nome: string) {
  const partes = nome.replace(/-/g, " ").split(" ").filter(Boolean);
  if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase();
  return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
}
