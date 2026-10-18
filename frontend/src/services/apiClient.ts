const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export async function checkApiHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error("Le backend n’est pas disponible.");
  }

  return response.json();
}