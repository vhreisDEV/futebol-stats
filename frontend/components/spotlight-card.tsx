"use client";

// Glow que segue o mouse dentro do card ao passar por cima.
// Adaptado de https://reactbits.dev/components/spotlight-card (licença MIT) --
// puro CSS + useRef, sem dependencia nova.
import { useRef, type ReactNode, type MouseEvent } from "react";
import "./spotlight-card.css";

interface SpotlightCardProps {
  children: ReactNode;
  className?: string;
  spotlightColor?: string;
}

export function SpotlightCard({
  children,
  className = "",
  spotlightColor = "rgba(212, 175, 55, 0.25)",
}: SpotlightCardProps) {
  const divRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!divRef.current) return;
    const rect = divRef.current.getBoundingClientRect();
    divRef.current.style.setProperty("--mouse-x", `${e.clientX - rect.left}px`);
    divRef.current.style.setProperty("--mouse-y", `${e.clientY - rect.top}px`);
    divRef.current.style.setProperty("--spotlight-color", spotlightColor);
  };

  return (
    <div ref={divRef} onMouseMove={handleMouseMove} className={`card-spotlight rounded-xl ${className}`.trim()}>
      {children}
    </div>
  );
}
