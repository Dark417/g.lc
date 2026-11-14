import { Component, OnInit, effect, inject, input, signal, untracked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService, fileToAttachment } from '../core/api.service';
import { IdentityService } from '../core/identity';
import { Attachment, ChatMessage, Conversation, StreamEvent, TraceEvent } from '../core/models';
import { MarkdownPipe } from '../shared/markdown.pipe';
import { VerdictCardComponent } from '../shared/verdict-card.component';

@Component({
  selector: 'app-chat-page',
  imports: [FormsModule, RouterLink, MarkdownPipe, VerdictCardComponent],
  template: `
    <div class="chat-layout">
      <aside class="sidebar">
        <button type="button" (click)="newChat()">+ New conversation</button>
        <ul class="conversations">
          @for (c of conversations(); track c.id) {
            <li [class.active]="c.id === sessionId()">
              <a routerLink="/chat" [queryParams]="{ c: c.id }">{{ c.title }}</a>
              <button type="button" class="icon" title="Delete" (click)="remove(c)">×</button>
            </li>
          } @empty {
            <li class="muted">No conversations yet.</li>
          }
        </ul>
      </aside>

      <section class="chat">
        <ul class="messages">
          @if (!messages().length) {
            <li class="hint">
              <p>Ask whether something is allowed, for example:</p>
              <ul>
                @for (s of suggestions; track s) {
                  <li><button type="button" class="link" (click)="input = s">{{ s }}</button></li>
                }
              </ul>
              @if (id.isAdmin()) {
                <p class="muted">As an admin you can also add rules ("add a hard rule that…") or attach a
                  policy file and say "ingest this" or "extract rules from this".</p>
              }
            </li>
          }
          @for (m of messages(); track $index) {
            <li [class]="'msg ' + m.role">
              @if (m.attachments?.length) {
                <div class="muted small">📎 {{ m.attachments!.join(', ') }}</div>
              }
              @for (v of m.verdicts; track v.assessment_id) {
                <app-verdict-card [verdict]="v" />
              }
              @if (m.text) {
                <div class="text" [innerHTML]="m.text | md"></div>
              } @else if (busy() && $last) {
                <div class="muted">Thinking…</div>
              }
              @if (showTrace() && m.trace?.length) {
                <ol class="trace">
                  @for (t of m.trace; track $index) {
                    <li [class]="t.type">{{ describe(t) }}</li>
                  }
                </ol>
              }
            </li>
          }
        </ul>

        @if (error(); as e) {
          <p class="error">{{ e }}</p>
        }

        <form class="composer" (ngSubmit)="send()">
          <textarea name="message" [(ngModel)]="input" rows="3" placeholder="Can we launch…?"
                    (keydown.enter)="onEnter($event)"></textarea>
          <div class="composer-row">
            <label class="file">
              📎 Attach
              <input type="file" multiple (change)="pick($event)" accept=".pdf,.docx,.md,.txt,.html,.htm" />
            </label>
            @for (f of files(); track f.name) {
              <span class="chip">{{ f.name }} <button type="button" class="icon" (click)="unpick(f)">×</button></span>
            }
            <span class="spacer"></span>
            <label class="small"><input type="checkbox" [checked]="showTrace()" (change)="showTrace.set(!showTrace())" /> trace</label>
            <button type="submit" [disabled]="busy() || !input.trim()">Send</button>
          </div>
        </form>
      </section>
    </div>
  `,
})
export class ChatPage implements OnInit {
  readonly id = inject(IdentityService);
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  /** `?c=<conversation id>` (withComponentInputBinding). */
  readonly routeId = input<string | undefined>(undefined, { alias: 'c' });

  readonly conversations = signal<Conversation[]>([]);
  readonly messages = signal<ChatMessage[]>([]);
  readonly sessionId = signal<string | null>(null);
  readonly files = signal<File[]>([]);
  readonly busy = signal(false);
  readonly error = signal<string | null>(null);
  readonly showTrace = signal(false);
  input = '';

  readonly suggestions = [
    'Can we launch a mobile game for 10-year-olds that collects email addresses at sign-up?',
    'Can we run an ad saying we are twice as fast as Acme Backup?',
    'We want to announce a 60% Black Friday discount tomorrow. Is that OK?',
    'Summarise the Data Privacy Standard.',
  ];

  constructor() {
    // React to the route only. Our own navigate(['/chat', id]) after a new session is a no-op here
    // because sessionId already matches.
    effect(() => {
      const rid = this.routeId();
      untracked(() => {
        if (rid && rid !== this.sessionId()) this.open(rid);
        if (!rid && this.sessionId() && !this.busy()) this.reset();
      });
    });
  }

  ngOnInit(): void {
    this.refreshConversations();
  }

  refreshConversations(): void {
    this.api.conversations().subscribe((c) => this.conversations.set(c));
  }

  open(id: string): void {
    this.sessionId.set(id);
    this.error.set(null);
    this.api.conversation(id).subscribe({
      next: (c) => this.messages.set(c.messages),
      error: () => {
        this.error.set('Conversation not found.');
        this.router.navigate(['/chat']);
      },
    });
  }

  reset(): void {
    this.sessionId.set(null);
    this.messages.set([]);
  }

  newChat(): void {
    this.reset();
    this.router.navigate(['/chat']);
  }

  remove(c: Conversation): void {
    if (!confirm(`Delete "${c.title}"?`)) return;
    this.api.deleteConversation(c.id).subscribe(() => {
      if (c.id === this.sessionId()) this.newChat();
      this.refreshConversations();
    });
  }

  pick(ev: Event): void {
    const el = ev.target as HTMLInputElement;
    this.files.update((f) => [...f, ...Array.from(el.files ?? [])]);
    el.value = '';
  }

  unpick(file: File): void {
    this.files.update((f) => f.filter((x) => x !== file));
  }

  onEnter(ev: Event): void {
    const e = ev as KeyboardEvent;
    if (!e.shiftKey) {
      e.preventDefault();
      this.send();
    }
  }

  async send(): Promise<void> {
    const text = this.input.trim();
    if (!text || this.busy()) return;
    const files = this.files();
    let attachments: Attachment[] = [];
    try {
      attachments = await Promise.all(files.map(fileToAttachment));
    } catch {
      this.error.set('Could not read the attached file.');
      return;
    }
    this.input = '';
    this.files.set([]);
    this.error.set(null);
    this.messages.update((m) => [
      ...m,
      { role: 'user', text, verdicts: [], attachments: files.map((f) => f.name) },
      { role: 'assistant', text: '', verdicts: [], trace: [] },
    ]);
    this.busy.set(true);

    this.api.stream(text, this.sessionId(), attachments).subscribe({
      next: (ev) => this.onEvent(ev),
      error: (e) => this.fail(e),
      complete: () => this.busy.set(false),
    });
  }

  private onEvent(ev: StreamEvent): void {
    switch (ev.type) {
      case 'session':
        if (ev.session_id !== this.sessionId()) {
          this.sessionId.set(ev.session_id);
          this.router.navigate(['/chat'], { queryParams: { c: ev.session_id }, replaceUrl: true });
        }
        break;
      case 'delta':
        this.patchLast((m) => ({ text: m.text + ev.text }));
        break;
      case 'verdict':
        this.patchLast((m) => ({ verdicts: [...m.verdicts, ev.verdict] }));
        break;
      case 'done':
        this.patchLast(() => ({ text: ev.reply }));
        this.refreshConversations();
        break;
      case 'error':
        this.fail(new Error(ev.message));
        break;
      default:
        this.patchLast((m) => ({ trace: [...(m.trace ?? []), ev] }));
    }
  }

  private patchLast(fn: (m: ChatMessage) => Partial<ChatMessage>): void {
    this.messages.update((all) => {
      const last = all[all.length - 1];
      return [...all.slice(0, -1), { ...last, ...fn(last) }];
    });
  }

  private fail(e: unknown): void {
    this.error.set(e instanceof Error ? e.message : String(e));
    this.busy.set(false);
  }

  describe(t: TraceEvent): string {
    return t.type === 'tool_call'
      ? `→ ${t.name}(${JSON.stringify(t.args ?? {})})`
      : `← ${t.name}: ${JSON.stringify(t.result).slice(0, 160)}`;
  }
}
