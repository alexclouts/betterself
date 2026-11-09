// src/api/auth.ts
const API_URL = import.meta.env.VITE_API_URL;

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