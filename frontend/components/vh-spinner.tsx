"use client";

import { useEffect, useRef, useState } from "react";
import "./vh-spinner.css";

const FRASES_PADRAO = [
  "Aquecendo o campo...",
  "Cobrando escanteio...",
  "Rolando a bola...",
  "Analisando a jogada...",
  "Apurando o placar...",
  "Batendo pênalti...",
  "Conferindo o VAR...",
  "Estudando o adversário...",
];

const ATRASO_INICIAL_MS = 3500; // carregamento rapido (a maioria) nem chega a ver isso
const VELOCIDADE_DIGITAR_MS = 40;
const VELOCIDADE_APAGAR_MS = 20;
const PAUSA_FRASE_COMPLETA_MS = 1400;

function esperar(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

interface VhSpinnerProps {
  className?: string;
  mensagens?: string[];
}

export function VhSpinner({ className = "", mensagens = FRASES_PADRAO }: VhSpinnerProps) {
  const [textoExibido, setTextoExibido] = useState(mensagens[0] ?? "");
  const textoRef = useRef(mensagens[0] ?? "");

  useEffect(() => {
    if (mensagens.length <= 1) return;

    let cancelado = false;
    textoRef.current = mensagens[0] ?? "";
    setTextoExibido(textoRef.current);

    const apagar = async () => {
      while (!cancelado && textoRef.current.length > 0) {
        textoRef.current = textoRef.current.slice(0, -1);
        setTextoExibido(textoRef.current);
        await esperar(VELOCIDADE_APAGAR_MS);
      }
    };

    const digitar = async (frase: string) => {
      for (let i = 1; i <= frase.length; i++) {
        if (cancelado) return;
        textoRef.current = frase.slice(0, i);
        setTextoExibido(textoRef.current);
        await esperar(VELOCIDADE_DIGITAR_MS);
      }
    };

    const loop = async () => {
      // Frase fixa (ja exibida por completo) durante o atraso inicial --
      // so entra o efeito de maquina de escrever se o carregamento
      // realmente demorar (ex.: cold start do backend no plano gratis).
      await esperar(ATRASO_INICIAL_MS);
      let indice = 0;
      while (!cancelado) {
        indice = (indice + 1) % mensagens.length;
        await apagar();
        if (cancelado) return;
        await digitar(mensagens[indice]);
        if (cancelado) return;
        await esperar(PAUSA_FRASE_COMPLETA_MS);
      }
    };

    loop();

    return () => {
      cancelado = true;
    };
  }, [mensagens]);

  return (
    <div className="flex flex-col items-center gap-2.5">
      <div className={`vh-spinner ${className}`.trim()} role="status" aria-label="Carregando">
        <span className="vh-spinner-label">VH</span>
      </div>
      {mensagens.length > 0 && (
        <p className="font-mono text-xs text-muted-foreground">
          {textoExibido}
          <span className="vh-spinner-cursor">|</span>
        </p>
      )}
    </div>
  );
}
