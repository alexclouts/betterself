import { useState } from "react";
import { useLocation } from "react-router-dom";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import { ResendVerificationButton } from "../../components/auth/ResendVerificationButton";

/*
 * Affichée après l'inscription : le compte doit être confirmé avec le lien
 * envoyé par courriel avant de pouvoir se connecter. L'adresse arrive par
 * l'état de navigation; si la page est rechargée ou ouverte directement,
 * l'utilisateur la saisit pour redemander un lien.
 */
export function CheckEmailPage() {
    const location = useLocation();
    const initialEmail = (location.state as { email?: string } | null)?.email ?? "";
    const [email, setEmail] = useState(initialEmail);

    return (
        <main className="flex min-h-screen items-center justify-center bg-background p-4">
            <Card className="w-full max-w-sm px-12 bg-surface">
                <div className="flex flex-col gap-6">
                    <h1>Vérifiez vos courriels</h1>

                    <p className="text-foreground">
                        {initialEmail ? (
                            <>Un lien de confirmation a été envoyé à <strong>{initialEmail}</strong>. </>
                        ) : (
                            <>Un lien de confirmation vous a été envoyé par courriel. </>
                        )}
                        Ouvrez-le pour activer votre compte, puis connectez-vous.
                    </p>

                    <p className="text-sm text-muted">
                        Rien reçu? Vérifiez vos courriels indésirables, ou demandez un nouveau lien.
                    </p>

                    {!initialEmail && (
                        <Input
                            placeholder="Courriel"
                            type="email"
                            autoComplete="username"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    )}

                    <ResendVerificationButton email={email} startWithCooldown={Boolean(initialEmail)} />

                    <div className="flex justify-center">
                        <a href="/login" className="text-primary-ink font-bold">Retour à la connexion</a>
                    </div>
                </div>
            </Card>
        </main>
    );
}
