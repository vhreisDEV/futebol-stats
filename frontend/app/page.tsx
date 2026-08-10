"use client";

import { useEffect, useState } from "react";

interface Time {
id: number;
nome: string;
}

export default function Home() {
const [times, setTimes] = useState<Time[]>([]);
const [carregando, setCarregando] = useState(true);
const [erro, setErro] = useState<string | null>(null);

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

if (carregando) return <p>Carregando times...</p>;
if (erro) return <p>Erro: {erro}</p>;

return (
<main>
<h1>Football Analytics Platform</h1>
<h2>Times</h2>
<ul>
{times.map((time) => (
<li key={time.id}>{time.nome}</li>
))}
</ul>
</main>
);
}