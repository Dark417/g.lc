// The only file that knows the backend URL and wire format.
import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface TraceEvent {
  type: 'tool_call' | 'tool_result' | 'agent_text';
  author: string;
  name?: string;
  args?: Record<string, unknown>;
  result?: unknown;
  text?: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  events: TraceEvent[];
}

export type StreamEvent =
  | TraceEvent
  | { type: 'delta'; text: string }
  | { type: 'done'; session_id: string; reply: string }
  | { type: 'error'; message: string };

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly http = inject(HttpClient);

  /** One request, one JSON reply with the full trace. */
  send(message: string, sessionId: string | null): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${environment.apiUrl}/api/v1/chat`, {
      message,
      session_id: sessionId,
    });
  }

  /**
   * Server-Sent Events over fetch. HttpClient can't consume a streaming body,
   * so this reads the ReadableStream and parses `data: <json>` frames by hand.
   */
  stream(message: string, sessionId: string | null): Observable<StreamEvent> {
    return new Observable<StreamEvent>((subscriber) => {
      const controller = new AbortController();
      (async () => {
        try {
          const res = await fetch(`${environment.apiUrl}/api/v1/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: sessionId }),
            signal: controller.signal,
          });
          if (!res.ok || !res.body) throw new Error(`backend ${res.status}`);
          const reader = res.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          for (;;) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            let idx: number;
            while ((idx = buffer.indexOf('\n\n')) >= 0) {
              const frame = buffer.slice(0, idx);
              buffer = buffer.slice(idx + 2);
              const line = frame.split('\n').find((l) => l.startsWith('data: '));
              if (line) subscriber.next(JSON.parse(line.slice(6)) as StreamEvent);
            }
          }
          subscriber.complete();
        } catch (err) {
          if (!controller.signal.aborted) subscriber.error(err);
        }
      })();
      return () => controller.abort();
    });
  }
}
