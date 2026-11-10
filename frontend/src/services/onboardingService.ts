const API_URL = import.meta.env.VITE_API_URL;

/**
 * Service pour gérer l'onboarding de l'utilisateur.
 */
export const onboardingService = {
    // Complète l'onboarding de l'utilisateur avec les informations fournies.
    async completeOnboarding(payload: {
        goal: string;
        name: string;
        birthYear: string;
        sex: string;
        heightCm: number;
        weightKg: number;
    }) {
        const token = localStorage.getItem("access_token");

        // Fait parvenir les données d'onboarding à l'API.
        const response = await fetch(`${API_URL}/onboarding`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const data = await response.json().catch(() => null);
            throw new Error(data?.detail ?? `Erreur ${response.status}`);
        }
        return response.json();
    },
};