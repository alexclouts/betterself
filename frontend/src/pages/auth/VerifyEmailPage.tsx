import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import { authService, IncorrectPasswordError } from "../../services/authService";
import { useAuthStore } from "../../stores/authStore";
import { useOnboarding } from "../../context/OnboardingContext";

const INVALID_LINK_MESSAGE = "Ce lien de vérification est invalide ou expiré.";

/*
 * Page ouverte depuis le lien reçu par courriel (/verify-email?token=...).
 * L'utilisateur entre son mot de passe pour confirmer l'adresse :
 *   - un filtre antipourriel qui ouvre le lien ne peut pas confirmer le compte;
 *   - quelqu'un qui aurait inscrit l'adresse d'une autre personne ne peut pas
 *     lui faire confirmer son compte, puisqu'elle ne connaît pas son mot de passe.
 * Une fois l'adresse confirmée, l'utilisateur est connecté directement.
 */
export function VerifyEmailPage() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token");

    const navigate = useNavigate();
    const setAuth = useAuthStore((state) => state.setAuth);
    const { refreshStatus } = useOnboarding();

    const [password, setPassword] = useState("");
    const [passwordError, setPasswordError] = useState<string | null>(null);
    const [linkError, setLinkError] = useState<string | null>(token ? null : INVALID_LINK_MESSAGE);
    const [isSubmitting, setIsSubmitting] = useState(false);

    async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();
        if (!token) return;
        setPasswordError(null);
        setIsSubmitting(true);

        try {
            const response = await authService.verifyEmail(token, password);
            setAuth(response.access_token);

            try {
                const onboardingStatus = await refreshStatus();
                navigate(onboardingStatus.is_complete ? "/" : "/onboarding", { replace: true });
            } catch {
                // L'adresse est confirmée et l'utilisateur connecté : l'accueil refera la vérification.
                navigate("/", { replace: true });
            }
        } catch (error) {
            if (error instanceof IncorrectPasswordError) {
                setPasswordError(error.message);
            } else {
                setLinkError(error instanceof Error ? error.message : INVALID_LINK_MESSAGE);
            }
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <main className="flex min-h-screen items-center justify-center bg-background p-4">
            <Card className="w-full max-w-sm px-12 bg-surface">
                {linkError ? (
                    <div className="flex flex-col gap-6">
                        <h1>Lien invalide</h1>
                        <p className="text-sm text-danger" role="alert">{linkError}</p>
                        <p className="text-foreground">
                            Le lien a peut-être expiré ou déjà été utilisé. Si votre adresse est déjà
                            confirmée, vous pouvez simplement vous connecter.
                        </p>
                        <div className="flex flex-col items-center gap-3">
                            <a href="/login" className="text-primary-ink font-bold">Se connecter</a>
                            <a href="/check-email" className="text-primary-ink font-bold">Recevoir un nouveau lien</a>
                        </div>
                    </div>
                ) : (
                    <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
                        <h1>Confirmer votre adresse</h1>
                        <p className="text-foreground">
                            Entrez le mot de passe choisi à l'inscription pour activer votre compte.
                        </p>

                        <Input
                            placeholder="Mot de passe"
                            type="password"
                            autoComplete="current-password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />

                        {passwordError && (
                            <p className="text-sm text-danger" role="alert">{passwordError}</p>
                        )}

                        <Button
                            className="font-bold mt-4 disabled:opacity-50"
                            disabled={isSubmitting || !password}
                        >
                            Confirmer mon adresse
                        </Button>
                    </form>
                )}
            </Card>
        </main>
    );
}
