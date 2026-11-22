import { defineConfig } from "orval";

// Configuration Orval pour générer le client API à partir du fichier OpenAPI.
export default defineConfig({
  betterself: {
    input: "../backend/src/betterself/openapi.json",
    output: {
      // Dossier distinct de `schemas` : sinon, l’index des routes écrase celui des types.
      target: "./src/api/generated/endpoints",
      schemas: "./src/api/generated",
      client: "axios",
      mode: "tags-split",
      override: {
        mutator: {
          path: "./src/api/axios.ts",
          name: "customInstance",
        },
      },
    },
  },
});