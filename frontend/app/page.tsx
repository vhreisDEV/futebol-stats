import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4 py-8 text-foreground">
      <div className="w-full max-w-sm text-center">
        <h1 className="font-heading text-4xl font-semibold uppercase tracking-wide sm:text-5xl">
          VEAGA
        </h1>
        <p className="mt-2 text-sm text-muted-foreground sm:text-base">
          Estatísticas e projeções de futebol.
        </p>

        <Link href="/brasileirao" className="mt-10 block">
          <Card className="text-left transition-colors hover:border-primary/50">
            <CardContent className="flex items-center justify-between gap-3">
              <span className="font-medium">Brasileirão Série A 2026</span>
              <span className="text-primary">→</span>
            </CardContent>
          </Card>
        </Link>
      </div>
    </main>
  );
}
