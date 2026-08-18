"use client";

import { useEffect, useState } from "react";
import "./vh-spinner.css";

const FRASES_PADRAO = [
  "Aquecendo o campo...",
  "Cobrando escanteio...",
  "Rolando a bola...",
  "Analisando a jogada...",
  "Apurando o placar...",
  "Batendo pênalti...",
  "Marcando em cima...",
];

interface VhSpinnerProps {
  className?: string;
  mensagens?: string[];
}

export function VhSpinner({ className = "", mensagens = FRASES_PADRAO }: VhSpinnerProps) {
  const [indice, setIndice] = useState(0);

  useEffect(() => {
    if (mensagens.length <= 1) return;

    // A maioria dos carregamentos daqui e rapido (menos de 1s) -- nao
    // vale girar frase pra quem nem vai ver. So comeca a trocar depois
    // de um tempo real de espera (ex.: cold start do backend no plano
    // gratis), pra quem pegou isso ter o que acompanhar.
    let intervalo: ReturnType<typeof setInterval> | undefined;

    const atraso = setTimeout(() => {
      intervalo = setInterval(() => {
        setIndice((i) => (i + 1) % mensagens.length);
      }, 2200);
    }, 3500);

    return () => {
      clearTimeout(atraso);
      if (intervalo) clearInterval(intervalo);
    };
  }, [mensagens]);

  return (
    <div className="flex flex-col items-center gap-2.5">
      <div className={`vh-spinner ${className}`.trim()} role="status" aria-label="Carregando">
        <span className="vh-spinner-label">VH</span>
      </div>
      {mensagens.length > 0 && (
        <p className="text-xs text-muted-foreground">{mensagens[indice]}</p>
      )}
    </div>
  );
}
