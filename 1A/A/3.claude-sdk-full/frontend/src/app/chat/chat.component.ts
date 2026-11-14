import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChatService, StreamEvent, TraceEvent } from './chat.service';

interface Msg {
  role: 'user' | 'assistant';
  text: string;
  events: TraceEvent[]; // the agent-loop trace behind an assistant message
}

@Component({
  selector: 'app-chat',
  imports: [FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css',
})
export class ChatComponent {
  private readonly chat = inject(ChatService);

  readonly messages = signal<Msg[]>([]);
  readonly sessionId = signal<string | null>(null);
  readonly busy = signal(false);
  readonly error = signal<string | null>(null);
  readonly streaming = signal(true);
  readonly showTrace = signal(true);
  input = '';

  send(): void {
    const text = this.input.trim();
    if (!text || this.busy()) return;
    this.input = '';
    this.error.set(null);
    this.messages.update((m) => [
      ...m,
      { role: 'user', text, events: [] },
      { role: 'assistant', text: '', events: [] },
    ]);
    this.busy.set(true);
    this.streaming() ? this.sendStreaming(text) : this.sendJson(text);
  }

  private sendJson(text: string): void {
    this.chat.send(text, this.sessionId()).subscribe({
      next: (res) => {
        this.sessionId.set(res.session_id);
        this.patchLast({ text: res.reply, events: res.events });
        this.busy.set(false);
      },
      error: (err) => this.fail(err),
    });
  }

  private sendStreaming(text: string): void {
    this.chat.stream(text, this.sessionId()).subscribe({
      next: (ev: StreamEvent) => {
        switch (ev.type) {
          case 'delta':
            this.patchLast((last) => ({ text: last.text + ev.text }));
            break;
          case 'done':
            this.sessionId.set(ev.session_id);
            this.patchLast({ text: ev.reply }); // authoritative final text
            break;
          case 'error':
            this.fail(new Error(ev.message));
            break;
          default:
            this.patchLast((last) => ({ events: [...last.events, ev] }));
        }
      },
      error: (err) => this.fail(err),
      complete: () => this.busy.set(false),
    });
  }

  private patchLast(patch: Partial<Msg> | ((last: Msg) => Partial<Msg>)): void {
    this.messages.update((m) => {
      const last = m[m.length - 1];
      const p = typeof patch === 'function' ? patch(last) : patch;
      return [...m.slice(0, -1), { ...last, ...p }];
    });
  }

  private fail(err: unknown): void {
    this.error.set(err instanceof Error ? err.message : String(err));
    this.busy.set(false);
  }

  label(ev: TraceEvent): string {
    switch (ev.type) {
      case 'tool_call':
        return `${ev.author} → ${ev.name}(${JSON.stringify(ev.args ?? {})})`;
      case 'tool_result':
        return `${ev.name} ⇒ ${JSON.stringify(ev.result).slice(0, 200)}`;
      default:
        return `${ev.author}: ${ev.text}`;
    }
  }
}
