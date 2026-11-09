// src/features/auth/LoginPage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../../api/auth";
import { useAuthStore } from "../../stores/authStore";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";

export function LoginPage() {
    // Navigation du routeur
    const navigate = useNavigate();
    const setAuth = useAuthStore((state) => state.setAuth);

    // États du formulaire
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();
        setError(null);
        setIsSubmitting(true);

        try {
        const response = await login({ email, password });
        setAuth(response.access_token);

        navigate("/", { replace: true });
        } catch {
        setError(
            "Courriel ou mot de passe invalide. Vérifie tes informations et réessaie."
        );
        } finally {
        setIsSubmitting(false);
        }
    }

    return (
        <main className="flex min-h-screen items-center justify-center bg-background p-4">
            <Card className="w-full max-w-sm p-6 bg-surface">
                <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
                    <div className="flex flex-col gap-1">
                        <h1 className="text-2xl font-bold text-foreground">BetterSelf</h1>
                    </div>

                    <Input
                    placeholder="Courriel"
                    type="email"
                    autoComplete="username"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    />

                    <Input
                    placeholder="Mot de passe"
                    type="password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    />

                    <Button className="bg-primary text-white font-bold hover:bg-primary-dark mt-4">
                    Se connecter
                    </Button>

                    <div className="flex justify-center">
                        <p className="text-foreground">Pas encore de compte ? <a href="/signup" className="text-primary font-bold">Créer un compte</a></p>
                    </div>

                </form>
            </Card>
        </main>
    );
}