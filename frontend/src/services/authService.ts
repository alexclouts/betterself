const API_URL = import.meta.env.VITE_API_URL;

type RegisterPayload = {
  email: string;
  password: string;
};

// Réalise l'appel à l'API pour l'inscription
export async function register(payload: RegisterPayload) {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        let message = "Impossible de créer le compte.";

        try {
            const data = await response.json();

            if (typeof data.detail === "string") {
                message = data.detail;
            }
        } catch {
        // La réponse n'était pas du JSON valide.
        }
        throw new Error(message);
    }
    return response.json();
}

// Fonction de connexion
export async function login(credentials: { email: string; password: string }) {
    const body = new URLSearchParams();
    body.set("username", credentials.email);
    body.set("password", credentials.password);

    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
    });
    if (!response.ok) {
        throw new Error("INVALID_CREDENTIALS");
    }
    return (await response.json()) as {
        access_token: string;
        token_type: string;
    };
}