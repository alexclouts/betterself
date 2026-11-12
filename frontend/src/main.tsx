import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from "react-router-dom";
import './index.css'
import App from './App.tsx'
import { OnboardingProvider } from "./context/OnboardingContext";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <OnboardingProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </OnboardingProvider>
  </StrictMode>,
)
