import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import './index.css'
import App from './App.tsx'
import { OnboardingProvider } from "./context/OnboardingContext";
import { queryClient } from "./lib/queryClient";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <OnboardingProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </OnboardingProvider>
    </QueryClientProvider>
  </StrictMode>
)
