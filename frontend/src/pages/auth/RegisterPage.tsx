
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import { useState } from "react";
import { authService } from "../../services/authService";
import { useNavigate } from "react-router-dom";

export function RegisterPage() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    async function handleSubmit(
        event: React.SubmitEvent<HTMLFormElement>
    ) {
        event.preventDefault();
        setError(null);

        // Validation des champs avant l'envoi du formulaire
        if (!email.trim()) {
            setError("Veuillez saisir une adresse courriel.");
            return;
        }
        if (password.length < 8) {
            setError("Le mot de passe doit contenir au moins 8 caractères.");
            return;
        }
        if (password !== confirmPassword) {
            setError("Les mots de passe ne correspondent pas.");
            return;
        }
        setIsSubmitting(true);

        try {
            await authService.register({ email, password });

            navigate("/login", {
                replace: true,
                state: {
                    message: "Compte créé avec succès. Connecte-toi maintenant.",
                },
            });
        } catch (registrationError) {
            setError(
                registrationError instanceof Error? registrationError.message: "Impossible de créer le compte. Réessaie plus tard."
            );
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <main className="flex min-h-screen items-center justify-center bg-background p-4">
            <Card className="w-full max-w-sm px-12 bg-surface">
                <form className="flex flex-col gap-6" onSubmit={handleSubmit}>

                    <div className="flex flex-col gap-1">
                        <h1 className="text-2xl font-bold text-foreground">Créer un compte</h1>
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
                        autoComplete="new-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <Input
                        placeholder="Confirmer le mot de passe"
                        type="password"
                        autoComplete="new-password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                    />

                    {error && (
                        <p className="text-sm text-danger" role="alert">
                            {error}
                        </p>
                    )}

                    <Button 
                        className="bg-primary text-white font-bold hover:bg-primary-dark mt-4"
                        disabled={isSubmitting}>
                        S'inscrire
                    </Button>

                    <div className="flex justify-center">
                        <p className="text-foreground">
                            Déjà un compte ? <a href="/login" className="text-primary font-bold">Se connecter</a>
                        </p>
                    </div>
                </form>
            </Card>
        </main>
    );
}