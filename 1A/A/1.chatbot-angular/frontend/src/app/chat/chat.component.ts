import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChatService } from './chat.service';

interface Msg {
  role: 'user' | 'assistant';
  text: string;
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
  input = '';

  send(): void {
    const text = this.input.trim();
    if (!text || this.busy()) return;
    this.input = '';
    this.error.set(null);
    this.messages.update((m) => [...m, { role: 'user', text }]);
    this.busy.set(true);

    this.chat.send(text, this.sessionId()).subscribe({
      next: (res) => {
        this.sessionId.set(res.session_id);
        this.messages.update((m) => [...m, { role: 'assistant', text: res.reply }]);
        this.busy.set(false);
      },
      error: (err) => {
        this.error.set(err?.message ?? String(err));
        this.busy.set(false);
      },
    });
  }
}
