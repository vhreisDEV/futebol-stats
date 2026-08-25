import { Bell } from "lucide-react";
import { TELEGRAM_BOT_USERNAME } from "@/lib/api";

export function TelegramCTA() {
  if (!TELEGRAM_BOT_USERNAME) return null;

  return (
    <a
      href={`https://t.me/${TELEGRAM_BOT_USERNAME}`}
      target="_blank"
      rel="noopener noreferrer"
      className="mt-4 inline-flex items-center gap-1.5 rounded-full border border-sky-500/40 bg-sky-500/10 px-3 py-1.5 text-xs font-semibold text-sky-400 transition-colors hover:bg-sky-500/20"
    >
      <Bell className="size-3.5" />
      Receba a Dica da Rodada no Telegram
    </a>
  );
}
