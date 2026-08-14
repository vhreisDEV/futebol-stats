import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";

export default function Jogadores() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4 py-8 text-foreground">
      <div className="max-w-sm text-center">
        <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide">Jogadores</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Artilheiros, assistências e estatísticas individuais chegam em breve.
        </p>
        <Link href="/brasileirao" className={`${buttonVariants({ variant: "outline" })} mt-6`}>
          ← Voltar para o Brasileirão
        </Link>
      </div>
    </main>
  );
}
