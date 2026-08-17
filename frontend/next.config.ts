import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // Libera acesso via tunel Cloudflare (cloudflared) para teste remoto --
  // o subdominio muda a cada execucao, entao usamos um curinga.
  allowedDevOrigins: ["*.trycloudflare.com"],
};

export default nextConfig;
