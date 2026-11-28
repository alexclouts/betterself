import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Card from "../../components/ui/Card";
import { authService } from "../../services/authService";

type Status = "pending" | "success" | "error";

/*
 * Page ouverte depuis le lien reçu par courriel (/verify-email?token=...).
 * Elle envoie le jeton au backend avec un POST. Le lien ne pointe pas
 * directement vers l'API : certains filtres antipourriels ouvrent les liens
 * des courriels, et ils ne doivent pas confirmer le compte à la place de l'utilisateur.
 */
export function VerifyEmailPage() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token");

    const [status, setStatus] = useState<Status>(token ? "pending" : "error");
    const [message, setMessage] = useState(
        token ? "" : "Ce lien de vérification est invalide ou expiré."
    );

    // Un jeton ne sert qu'une fois. En développement, StrictMode exécute les effets
    // deux fois : sans cette garde, le second appel échouerait et afficherait une erreur.
    const hasSubmitted = useRef(false);

    useEffect(() => {
        if (!token || hasSubmitted.current) return;
        hasSubmitted.current = true;

        authService
            .verifyEmail(token)
            .then((response) => {
                setStatus("success");
                setMessage(response.message);
            })
            .catch((error: unknown) => {
                setStatus("error");
                setMessage(error instanceof Error ? error.message : "Impossible de confirmer l'adresse courriel.");
            });
    }, [token]);

    return (
        <main className="flex min-h-screen items-center justify-center bg-background p-4">
            <Card className="w-full max-w-sm px-12 bg-surface">
                <div className="flex flex-col gap-6" aria-live="polite">
                    {status === "pending" && (
                        <>
                            <h1>Confirmation en cours</h1>
                            <p className="text-foreground">Un instant…</p>
                        </>
                    )}

                    {status === "success" && (
                        <>
                            <h1>Adresse confirmée</h1>
                            <p className="text-foreground">{message}</p>
                            <a
                                href="/login"
                                className="rounded-2xl bg-primary p-2 text-center font-bold text-white shadow-sm hover:bg-primary-dark"
                            >
                                Se connecter
                            </a>
                        </>
                    )}

                    {status === "error" && (
                        <>
                            <h1>Lien invalide</h1>
                            <p className="text-sm text-danger" role="alert">{message}</p>
                            <p className="text-foreground">
                                Le lien a peut-être expiré ou déjà été utilisé. Si votre adresse est déjà
                                confirmée, vous pouvez simplement vous connecter.
                            </p>
                            <div className="flex flex-col items-center gap-3">
                                <a href="/login" className="text-primary-ink font-bold">Se connecter</a>
                                <a href="/check-email" className="text-primary-ink font-bold">Recevoir un nouveau lien</a>
                            </div>
                        </>
                    )}
                </div>
            </Card>
        </main>
    );
}
