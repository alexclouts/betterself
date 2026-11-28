import { useEffect, useState } from "react";
import Button from "../ui/Button";
import { authService } from "../../services/authService";
import { useToastStore } from "../../stores/toastStore";

// Même délai que email_verification_resend_seconds côté backend : un clic plus tôt
// ne renverrait rien, on évite donc de laisser croire qu'un courriel est parti.
const COOLDOWN_SECONDS = 60;

type Props = {
    email: string;
    // Le lien vient d'être envoyé (par exemple juste après l'inscription) : on attend avant de proposer un renvoi.
    startWithCooldown?: boolean;
};

// Bouton pour recevoir un nouveau lien de vérification par courriel.
export function ResendVerificationButton({ email, startWithCooldown = false }: Props) {
    const [secondsLeft, setSecondsLeft] = useState(startWithCooldown ? COOLDOWN_SECONDS : 0);
    const [isSending, setIsSending] = useState(false);

    useEffect(() => {
        if (secondsLeft <= 0) return;
        const timer = setTimeout(() => setSecondsLeft((seconds) => seconds - 1), 1000);
        return () => clearTimeout(timer);
    }, [secondsLeft]);

    async function handleClick() {
        setIsSending(true);
        try {
            const response = await authService.resendVerification(email.trim());
            useToastStore.getState().showToast(response.message);
            setSecondsLeft(COOLDOWN_SECONDS);
        } catch (error) {
            useToastStore.getState().showToast(
                error instanceof Error ? error.message : "Impossible d'envoyer le courriel.",
                { variant: "error" },
            );
        } finally {
            setIsSending(false);
        }
    }

    return (
        <Button
            type="button"
            variant="ghost"
            className="font-bold disabled:opacity-50"
            disabled={isSending || secondsLeft > 0 || !email.trim()}
            onClick={handleClick}
        >
            {secondsLeft > 0 ? `Renvoyer le lien (${secondsLeft} s)` : "Renvoyer le lien"}
        </Button>
    );
}
