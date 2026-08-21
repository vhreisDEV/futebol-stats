const DIAS_SEMANA = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

/**
 * Formata "AAAA-MM-DD" em "Dia, DD/MM/AAAA", opcionalmente com horário
 * (aceita "HH:MM" ou "HH:MM:SS", corta pros minutos). O dia da semana e'
 * calculado a partir dos componentes ano/mes/dia direto (nao via
 * `new Date(dataStr)`), pra nao correr risco do parse de string ISO
 * escorregar de dia dependendo do fuso do navegador de quem acessa.
 */
export function formatarDataHora(dataStr: string | null, horaStr?: string | null) {
  if (!dataStr) return "Data a definir";

  const partes = dataStr.split("-");
  if (partes.length !== 3) return dataStr;

  const [ano, mes, dia] = partes;
  const diaSemana = DIAS_SEMANA[new Date(Number(ano), Number(mes) - 1, Number(dia)).getDay()];
  const dataFormatada = `${diaSemana}, ${dia}/${mes}/${ano}`;

  return horaStr ? `${dataFormatada} — ${horaStr.slice(0, 5)}` : dataFormatada;
}
