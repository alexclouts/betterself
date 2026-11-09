import { Routes, Route } from "react-router-dom";
import { LoginPage } from "./features/auth/LoginPage";
import { RegisterPage } from "./features/auth/RegisterPage";
import { HomePage } from "./features/home/HomePage";
import { ProtectedRoute } from "./routes/ProtectedRoutes";

// Composant principal de l'application BetterSelf.
function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
            <Route element={<ProtectedRoute />}>
        <Route path="/" element={<HomePage />} />
      </Route>

      <Route path="*" element={<LoginPage />} />
    </Routes>
  );
}


export default App;