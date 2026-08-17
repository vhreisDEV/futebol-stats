"use client";

import { Fragment, useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { corTime, iniciais } from "@/lib/times-visual";

interface Perfil {
  id: number;
  nome: string;
  posicao: string | null;
  time_id: number | null;
  time_nome: string | null;
}

interface JogoJogador {
  id: number;
  partida_id: number;
  data: string;
  adversario: string;
  casa_ou_fora: string;
  minutos_jogados: number | null;
  gols: number;
  assistencias: number;
  chutes: number | null;
  chutes_gol: number | null;
  desarmes: number | null;
  faltas_cometidas: number | null;
  faltas_sofridas: number | null;
  cartoes_amarelos: number;
  cartoes_vermelhos: number;
}

interface LinhaTabela {
  label: string;
  chave: keyof JogoJogador;
}

const linhasTabela: LinhaTabela[] = [
  { label: "Minutos", chave: "minutos_jogados" },
  { label: "Gols", chave: "gols" },
  { label: "Assistências", chave: "assistencias" },
  { label: "Chutes", chave: "chutes" },
  { label: "Chutes ao gol", chave: "chutes_gol" },
  { label: "Desarmes", chave: "desarmes" },
  { label: "Faltas cometidas", chave: "faltas_cometidas" },
  { label: "Faltas sofridas", chave: "faltas_sofridas" },
  { label: "Cartões amarelos", chave: "cartoes_amarelos" },
  { label: "Cartões vermelhos", chave: "cartoes_vermelhos" },
];

function formatarData(dataStr: string) {
  const partes = dataStr.split("-");
  if (partes.length === 3) {
    const [ano, mes, dia] = partes;
    return `${dia}/${mes}/${ano}`;
  }
  return dataStr;
}

function valorOuTraco(valor: number | null) {
  return valor === null || valor === undefined ? "—" : valor;
}

function media(jogos: JogoJogador[], chave: keyof JogoJogador) {
  const valores = jogos
    .map((jogo) => jogo[chave])
    .filter((valor): valor is number => typeof valor === "number");

  if (valores.length === 0) return null;

  const soma = valores.reduce((acc, valor) => acc + valor, 0);
  return Math.round((soma / valores.length) * 10) / 10;
}

export function JogadorModal({
  jogadorId,
  onClose,
}: {
  jogadorId: number | null;
  onClose: () => void;
}) {
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [jogos, setJogos] = useState<JogoJogador[]>([]);
  const [quantidade, setQuantidade] = useState(10);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (jogadorId === null) return;

    setCarregando(true);
    setErro(null);

    Promise.all([
      fetch(`http://127.0.0.1:8000/jogadores/${jogadorId}`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar jogador");
        return r.json();
      }),
      fetch(`http://127.0.0.1:8000/jogadores/${jogadorId}/jogos?quantidade=${quantidade}`).then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar jogos do jogador");
        return r.json();
      }),
    ])
      .then(([dadosPerfil, dadosJogos]) => {
        setPerfil(dadosPerfil);
        setJogos(dadosJogos);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, [jogadorId, quantidade]);

  if (jogadorId === null) return null;

  const cores = corTime(perfil?.time_nome ?? "");
  const larguraLabel = 130;
  const larguraMedia = 60;
  const larguraJogo = 92;
  const larguraFixa = larguraLabel + larguraMedia;
  const larguraGrade = larguraFixa + jogos.length * larguraJogo;

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-h-[85vh] w-auto max-w-[95vw] overflow-auto sm:max-w-[95vw]">
        <DialogHeader>
          <div className="flex items-center gap-2">
            {perfil && (
              <span
                className={`flex size-7 shrink-0 items-center justify-center rounded-full border-2 text-[10px] font-bold ${cores.textoEscuro ? "text-black" : "text-white"}`}
                style={{ backgroundColor: cores.fundo, borderColor: cores.borda }}
              >
                {iniciais(perfil.time_nome ?? perfil.nome)}
              </span>
            )}
            <DialogTitle className="uppercase tracking-wide">
              {perfil ? `${perfil.nome} — Estatísticas Detalhadas` : "Carregando…"}
            </DialogTitle>
          </div>
          {perfil && (
            <p className="text-xs text-muted-foreground">
              {perfil.posicao ?? "—"} · {perfil.time_nome ?? "Sem clube"}
            </p>
          )}
        </DialogHeader>

        <div className="flex items-center justify-between gap-3">
          <span className="text-xs text-muted-foreground">Período de análise</span>
          <ToggleGroup
            variant="outline"
            size="sm"
            value={[String(quantidade)]}
            onValueChange={(v: string[]) => v[0] && setQuantidade(Number(v[0]))}
          >
            <ToggleGroupItem value="5">Últimos 5</ToggleGroupItem>
            <ToggleGroupItem value="10">Últimos 10</ToggleGroupItem>
            <ToggleGroupItem value="20">Últimos 20</ToggleGroupItem>
            <ToggleGroupItem value="30">Últimos 30</ToggleGroupItem>
          </ToggleGroup>
        </div>

        {erro && <p className="text-destructive">Erro: {erro}</p>}

        {!carregando && !erro && jogos.length === 0 && (
          <p className="py-6 text-center text-sm text-muted-foreground">
            Nenhum jogo encontrado nesse período.
          </p>
        )}

        {jogos.length > 0 && (
          <div style={{ minWidth: larguraGrade }}>
            <div
              className="flex items-center gap-2 pb-1.5 text-[10px] font-medium uppercase tracking-wide text-muted-foreground"
              style={{ paddingLeft: larguraFixa }}
            >
              <span>Último jogo</span>
              <div className="h-px flex-1 bg-border" />
              <span>Mais antigo</span>
            </div>

            <div className="overflow-hidden rounded-lg ring-1 ring-border">
              <div
                className="grid gap-px bg-border text-xs"
                style={{
                  gridTemplateColumns: `${larguraLabel}px ${larguraMedia}px repeat(${jogos.length}, ${larguraJogo}px)`,
                }}
              >
                <div className="bg-card px-2 py-2" />
                <div className="border-l-2 border-primary bg-primary/10 px-2 py-2 text-center font-semibold text-primary">
                  Média
                </div>
                {jogos.map((jogo, index) => (
                  <div key={index} className="bg-card px-2 py-2 text-center">
                    <p className="text-[11px] text-muted-foreground">{formatarData(jogo.data)}</p>
                    <p className="mt-0.5 truncate font-medium text-foreground">{jogo.adversario}</p>
                    <p className="mt-0.5 text-[10px] text-muted-foreground">
                      {jogo.casa_ou_fora === "casa" ? "Casa" : "Fora"}
                    </p>
                  </div>
                ))}

                {linhasTabela.map((linha) => (
                  <Fragment key={linha.chave}>
                    <div className="bg-background px-2 py-2 text-[11px] text-muted-foreground">
                      {linha.label}
                    </div>
                    <div className="border-l-2 border-primary bg-primary/10 px-2 py-2 text-center font-mono font-semibold tabular-nums text-primary">
                      {valorOuTraco(media(jogos, linha.chave))}
                    </div>
                    {jogos.map((jogo, index) => {
                      const valor = jogo[linha.chave];
                      return (
                        <div
                          key={`${linha.chave}-${index}`}
                          className="bg-background px-2 py-2 text-center font-mono tabular-nums text-foreground"
                        >
                          {valor === null ? "—" : valor}
                        </div>
                      );
                    })}
                  </Fragment>
                ))}
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
