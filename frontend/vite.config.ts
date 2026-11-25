// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";
import basicSsl from "@vitejs/plugin-basic-ssl";

/*
 * Mode « lan » (npm run dev:lan) : pour tester sur une tablette ou un téléphone du
 * même réseau Wi-Fi. La caméra exige HTTPS hors de localhost : le serveur est servi
 * en HTTPS (certificat autosigné) et l'API passe par le proxy /api, pour que
 * l'appareil n'ait qu'une seule adresse à joindre.
 */
// Même port que le serveur de développement habituel (vite --port 8080) : arrêter
// celui-ci avant de lancer le mode « lan ».
const API_PROXY_TARGET = process.env.API_PROXY_TARGET ?? "http://127.0.0.1:8000";

export default defineConfig(({ mode }) => ({
  server:
    mode === "lan"
      ? {
          host: true,
          port: 8080,
          strictPort: true,
          proxy: {
            "/api": {
              target: API_PROXY_TARGET,
              changeOrigin: true,
              rewrite: (path) => path.replace(/^\/api/, ""),
            },
          },
        }
      : undefined,
  plugins: [
    ...(mode === "lan" ? [basicSsl()] : []),
    react(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg"],
      manifest: {
        name: "BetterSelf",
        short_name: "BetterSelf",
        description:
          "Suivi nutritionnel, objectifs et journal alimentaire.",
        theme_color: "#0f172a",
        background_color: "#ffffff",
        display: "standalone",
        start_url: "/",
        icons: [
          {
            src: "/icons/icon-192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "/icons/icon-512.png",
            sizes: "512x512",
            type: "image/png",
          },
        ],
      },
    }),
  ],
}));
