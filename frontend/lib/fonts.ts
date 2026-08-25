import { Space_Mono } from "next/font/google";

// Fonte usada pontualmente pra reforcar a linha visual "sumula oficial"
// (documento de partida) -- mais cara de maquina de escrever/formulario
// carbonado do que o Geist Mono padrao do site. So aplicada onde esse
// efeito faz sentido (PartidaModal, Analise IA), nao em todo o site.
export const sumulaMono = Space_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-sumula-mono",
});
