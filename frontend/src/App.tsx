import Button from "./components/ui/Button";
import Card from "./components/ui/Card";
import Input from "./components/ui/Input";
import { Routes, Route } from "react-router-dom";
import { LoginPage } from "./features/auth/LoginPage";

// Composant principal de l'application BetterSelf.
function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="*" element={<LoginPage />} />
    </Routes>
  );
}


export default App;