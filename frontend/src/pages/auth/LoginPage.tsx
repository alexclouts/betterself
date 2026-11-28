// src/features/auth/LoginPage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService, EmailNotVerifiedError } from "../../services/authService";
import { ResendVerificationButton } from "../../components/auth/ResendVerificationButton";
import { useAuthStore } from "../../stores/authStore";
import { useOnboarding } from "../../context/OnboardingContext";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import logo from "../../assets/logo.png";

export function LoginPage() {
    // Navigation du routeur
    const navigate = useNavigate();
    const setAuth = useAuthStore((state) => state.setAuth);

    
    // États du formulaire
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState<string | null>(null);
    // Le mot de passe est bon, mais l'adresse n'est pas confirmée : on propose de renvoyer le lien.
    const [isUnverified, setIsUnverified] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Récupère la fonction pour rafraîchir le statut de l'onboarding utilisateur.
    const { refreshStatus } = useOnboarding();

    async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();
        setError(null);
        setIsUnverified(false);
        setIsSubmitting(true);

        try {
            const response = await authService.login({ email, password });
            setAuth(response.access_token);

            try {
                const onboardingStatus = await refreshStatus();
                // Redirige l'utilisateur en fonction de l'état de l'onboarding.
                navigate(
                    onboardingStatus.is_complete ? "/" : "/onboarding",
                    { replace: true }
                );
            } catch(error) {
                // Si la vérification du statut de l'onboarding échoue, on affiche un message d'erreur.
                setError(
                    "Connexion réussie, mais impossible de vérifier votre onboarding. Réessayez."
                );
            }
        } catch (loginError) {
            if (loginError instanceof EmailNotVerifiedError) {
                setIsUnverified(true);
                setError(loginError.message);
                return;
            }
            // Si la connexion échoue, on affiche un message d'erreur.
            setError("Impossible de vous connecter. Vérifiez vos identifiants.");
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <main className="flex min-h-screen items-center justify-center bg-background p-4">
            <Card className="w-full max-w-sm p-6 bg-surface">
                <form className="flex flex-col gap-6" onSubmit={handleSubmit}>

                    <div className="flex flex-col items-center gap-1">
                        <img src={logo} alt="" className="h-28 w-28" />
                        <h1 className="mt-0 font-semibold tracking-tight text-foreground">BetterSelf</h1>
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

                    {error && (
                        <p className="text-sm text-danger" role="alert">
                            {error}
                        </p>
                    )}

                    {isUnverified && <ResendVerificationButton email={email} />}

                    <Button className="bg-primary text-white font-bold hover:bg-primary-dark mt-4">
                    Se connecter
                    </Button>

                    <div className="flex justify-center">
                        <p className="text-foreground">Pas encore de compte ? <a href="/register" className="text-primary-ink font-bold">Créer un compte</a></p>
                    </div>

                </form>
            </Card>
        </main>
    );
}