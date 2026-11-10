import { useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";
import { authService } from "../../services/authService";


export function HomePage() {
    const navigate = useNavigate();

    function handleLogout() {
        authService.logout();
        navigate("/login", { replace: true });
    }

    return (
    <div>
      <header>
        <h1>Welcome to the Home Page</h1>

        <Button variant="secondary" onClick={handleLogout} className="mt-4">
          Se déconnecter
        </Button>
      </header>
    </div>
    );
}