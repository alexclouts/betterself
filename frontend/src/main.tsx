import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import "@fontsource-variable/inter/index.css";
import "@fontsource/poppins/500.css";
import "@fontsource/poppins/600.css";
import './index.css'
import { OnboardingProvider } from "./context/OnboardingContext";
import { queryClient } from "./lib/queryClient";
import { router } from "./routes/AppRoutes";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <OnboardingProvider>
        <RouterProvider router={router} />
      </OnboardingProvider>
    </QueryClientProvider>
  </StrictMode>
)
