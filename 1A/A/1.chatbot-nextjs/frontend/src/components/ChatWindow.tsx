"use client";

import { FormEvent, useState } from "react";
import { sendChat } from "@/lib/api";

type Msg = { role: "user" | "assistant"; text: string };

export default function ChatWindow() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setError(null);
    setMessages((m) => [...m, { role: "user", text }]);
    setBusy(true);
    try {
      const res = await sendChat(text, sessionId);
      setSessionId(res.session_id);
      setMessages((m) => [...m, { role: "assistant", text: res.reply }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="chat">
      <ul className="messages">
        {messages.map((m, i) => (
          <li key={i} className={m.role}>
            {m.text}
          </li>
        ))}
        {busy && <li className="assistant muted">…</li>}
      </ul>
      {error && <p className="error">{error}</p>}
      <form onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Say something"
          autoFocus
        />
        <button disabled={busy || !input.trim()}>Send</button>
      </form>
      <p className="muted">session: {sessionId ?? "new"}</p>
    </section>
  );
}
