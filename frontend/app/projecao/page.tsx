"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Time {
  id: number;
  nome: string;
}

interface Projecao {
  time_mandante: string;
  time_visitante: string;
  data_referencia: string;
  gols: {
    mandante: number | null;
    visitante: number | null;
  };
  resultado: {
    vitoria_mandante: number | null;
    empate: number | null;
    vitoria_visitante: number | null;
  };
  escanteios: {
    mandante: number | null;
    visitante: number | null;
    total: number | null;
    linha_referencia: number | null;
    tendencia: string | null;
  };
  cartoes: {
    amarelos_mandante: number | null;
    amarelos_visitante: number | null;
    vermelhos_mandante: number | null;
    vermelhos_visitante: number | null;
    total: number | null;
    linha_referencia: number | null;
    tendencia: string | null;
  };
  chutes: {
    totais_mandante: number | null;
    totais_visitante: number | null;
    ao_gol_mandante: number | null;
    ao_gol_visitante: number | null;
    primeiro_tempo_mandante: number | null;
    primeiro_tempo_visitante: number | null;
  };
}

function valorOuTraco(valor: number | null) {
  return valor === null || valor === undefined ? "—" : valor;
}

function placarArredondado(valor: number | null) {
  return valor === null || valor === undefined ? "—" : Math.round(valor);
}

function Card({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
        {titulo}
      </h3>
      {children}
    </div>
  );
}

function LinhaComparativa({
  label,
  valorMandante,
  valorVisitante,
}: {
  label: string;
  valorMandante: number | null;
  valorVisitante: number | null;
}) {
  const aMaior =
    typeof valorMandante === "number" && typeof valorVisitante === "number" && valorMandante > valorVisitante;
  const bMaior =
    typeof valorMandante === "number" && typeof valorVisitante === "number" && valorVisitante > valorMandante;

  return (
    <div className="grid grid-cols-3 border-t border-slate-800 px-1 py-3 text-sm first:border-t-0">
      <span className={aMaior ? "font-semibold text-green-400" : "text-slate-300"}>
        {valorOuTraco(valorMandante)}
      </span>
      <span className="text-center text-slate-500">{label}</span>
      <span className={`text-right ${bMaior ? "font-semibold text-green-400" : "text-slate-300"}`}>
        {valorOuTraco(valorVisitante)}
      </span>
    </div>
  );
}

function TendenciaTexto({
  total,
  linhaReferencia,
  tendencia,
  unidade,
}: {
  total: number | null;
  linhaReferencia: number | null;
  tendencia: string | null;
  unidade: string;
}) {
  if (total === null || linhaReferencia === null || !tendencia) {
    return <p className="text-sm text-slate-500">Sem dado suficiente para calcular tendência.</p>;
  }

  const palavra = tendencia === "over" ? "mais de" : "menos de";

  return (
    <p className="text-sm text-slate-300">
      Tendência de <span className="font-semibold text-white">{palavra} {linhaReferencia}</span> {unidade} na
      partida (total esperado: <span className="font-semibold text-white">{total}</span>).
    </p>
  );
}

export default function ProjecaoPreJogo() {
  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const [mandanteId, setMandanteId] = useState<string>("");
  const [visitanteId, setVisitanteId] = useState<string>("");

  const [projecao, setProjecao] = useState<Projecao | null>(null);
  const [carregandoProjecao, setCarregandoProjecao] = useState(false);
  const [erroProjecao, setErroProjecao] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/times/")
      .then((resposta) => {
        if (!resposta.ok) {
          throw new Error("Erro ao buscar times");
        }
        return resposta.json();
      })
      .then((dados) => {
        setTimes(dados);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, []);

  useEffect(() => {
    if (!mandanteId || !visitanteId || mandanteId === visitanteId) {
      setProjecao(null);
      return;
    }

    setCarregandoProjecao(true);
    setErroProjecao(null);

    fetch(`http://127.0.0.1:8000/projecoes/${mandanteId}/${visitanteId}`)
      .then((resposta) => {
        if (!resposta.ok) {
          throw new Error("Erro ao buscar projeção");
        }
        return resposta.json();
      })
      .then((dados) => {
        setProjecao(dados);
        setCarregandoProjecao(false);
      })
      .catch((err) => {
        setErroProjecao(err.message);
        setCarregandoProjecao(false);
      });
  }, [mandanteId, visitanteId]);

  if (carregando) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-300">
        <p>Carregando times...</p>
      </main>
    );
  }

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-red-400">
        <p>Erro: {erro}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-3xl">
        <Link href="/" className="text-sm text-slate-400 underline hover:text-white">
          ← Voltar para a lista de times
        </Link>

        <h1 className="mt-4 text-3xl font-bold tracking-tight">Projeção Pré-Jogo</h1>
        <p className="mt-2 text-slate-400">
          Selecione mandante e visitante para ver a projeção estatística do confronto.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm text-slate-400">Mandante</label>
            <select
              value={mandanteId}
              onChange={(e) => setMandanteId(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-slate-100"
            >
              <option value="">Selecione um time</option>
              {times.map((time) => (
                <option key={time.id} value={time.id}>
                  {time.nome}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-400">Visitante</label>
            <select
              value={visitanteId}
              onChange={(e) => setVisitanteId(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-slate-100"
            >
              <option value="">Selecione um time</option>
              {times.map((time) => (
                <option key={time.id} value={time.id}>
                  {time.nome}
                </option>
              ))}
            </select>
          </div>
        </div>

        {mandanteId && visitanteId && mandanteId === visitanteId && (
          <p className="mt-8 text-amber-400">Selecione dois times diferentes.</p>
        )}

        {carregandoProjecao && <p className="mt-8 text-slate-400">Calculando projeção...</p>}

        {erroProjecao && <p className="mt-8 text-red-400">Erro: {erroProjecao}</p>}

        {projecao && (
          <div className="mt-10 grid gap-6">
            <div className="rounded-lg border border-indigo-800 bg-indigo-950/40 p-5 text-center">
              <p className="text-xs uppercase tracking-wide text-slate-400">Placar mais provável</p>
              <p className="mt-2 text-2xl font-bold">
                {projecao.time_mandante} {placarArredondado(projecao.gols.mandante)}
                {" x "}
                {placarArredondado(projecao.gols.visitante)} {projecao.time_visitante}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                Gols esperados (média): {valorOuTraco(projecao.gols.mandante)} x {valorOuTraco(projecao.gols.visitante)}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                Referência: {projecao.data_referencia}
              </p>
            </div>

            <Card titulo="Probabilidade de resultado">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-green-400">
                    {valorOuTraco(projecao.resultado.vitoria_mandante)}%
                  </p>
                  <p className="mt-1 text-xs text-slate-400">{projecao.time_mandante}</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-300">
                    {valorOuTraco(projecao.resultado.empate)}%
                  </p>
                  <p className="mt-1 text-xs text-slate-400">Empate</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-400">
                    {valorOuTraco(projecao.resultado.vitoria_visitante)}%
                  </p>
                  <p className="mt-1 text-xs text-slate-400">{projecao.time_visitante}</p>
                </div>
              </div>
            </Card>

            <Card titulo="Escanteios esperados">
              <LinhaComparativa
                label="Escanteios"
                valorMandante={projecao.escanteios.mandante}
                valorVisitante={projecao.escanteios.visitante}
              />
              <div className="mt-3 border-t border-slate-800 pt-3">
                <TendenciaTexto
                  total={projecao.escanteios.total}
                  linhaReferencia={projecao.escanteios.linha_referencia}
                  tendencia={projecao.escanteios.tendencia}
                  unidade="escanteios"
                />
              </div>
            </Card>

            <Card titulo="Cartões esperados">
              <LinhaComparativa
                label="Amarelos"
                valorMandante={projecao.cartoes.amarelos_mandante}
                valorVisitante={projecao.cartoes.amarelos_visitante}
              />
              <LinhaComparativa
                label="Vermelhos"
                valorMandante={projecao.cartoes.vermelhos_mandante}
                valorVisitante={projecao.cartoes.vermelhos_visitante}
              />
              <div className="mt-3 border-t border-slate-800 pt-3">
                <TendenciaTexto
                  total={projecao.cartoes.total}
                  linhaReferencia={projecao.cartoes.linha_referencia}
                  tendencia={projecao.cartoes.tendencia}
                  unidade="cartões"
                />
              </div>
            </Card>

            <Card titulo="Chutes esperados">
              <LinhaComparativa
                label="Chutes totais"
                valorMandante={projecao.chutes.totais_mandante}
                valorVisitante={projecao.chutes.totais_visitante}
              />
              <LinhaComparativa
                label="Chutes ao gol"
                valorMandante={projecao.chutes.ao_gol_mandante}
                valorVisitante={projecao.chutes.ao_gol_visitante}
              />
              <LinhaComparativa
                label="Chutes 1º tempo"
                valorMandante={projecao.chutes.primeiro_tempo_mandante}
                valorVisitante={projecao.chutes.primeiro_tempo_visitante}
              />
            </Card>
          </div>
        )}
      </div>
    </main>
  );
}