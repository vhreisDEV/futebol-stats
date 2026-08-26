import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono, Oswald } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const oswald = Oswald({
  variable: "--font-oswald",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

const URL_SITE = "https://veaga-psi.vercel.app";

export const metadata: Metadata = {
  metadataBase: new URL(URL_SITE),
  title: "VEAGA — Football Data & Analytics",
  description: "Football Data & Analytics.",
  openGraph: {
    title: "VEAGA — Football Data & Analytics",
    description: "Estatísticas e Análise IA do Brasileirão e outras ligas.",
    url: URL_SITE,
    siteName: "VEAGA",
    images: [{ url: "/logo_VEAGA.jpg", width: 1024, height: 572 }],
    locale: "pt_BR",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "VEAGA — Football Data & Analytics",
    description: "Estatísticas e Análise IA do Brasileirão e outras ligas.",
    images: ["/logo_VEAGA.jpg"],
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  colorScheme: "dark",
  themeColor: "#0A0A0A",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="pt-BR"
      className={`dark ${geistSans.variable} ${geistMono.variable} ${oswald.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
