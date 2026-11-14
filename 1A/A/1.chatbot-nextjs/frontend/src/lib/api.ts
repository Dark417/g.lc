// The only module that knows the backend URL and its wire format.

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ChatResponse = { session_id: string; reply: string };

export async function sendChat(
  message: string,
  sessionId: string | null,
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!res.ok) throw new Error(`backend ${res.status}: ${await res.text()}`);
  return res.json();
}
