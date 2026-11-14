import { DatePipe, DecimalPipe } from '@angular/common';
import { Component, OnInit, effect, inject, input, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { IdentityService } from '../core/identity';
import { DocumentRecord, RuleIn } from '../core/models';

@Component({
  selector: 'app-documents-page',
  imports: [FormsModule, RouterLink, DatePipe, DecimalPipe],
  template: `
    <div class="two-col">
      <section>
        <h2>Compliance documents</h2>
        @if (id.isAdmin()) {
          <form class="card upload" (ngSubmit)="upload()">
            <strong>Upload</strong>
            <input type="file" name="file" accept=".pdf,.docx,.md,.txt,.html,.htm" (change)="pick($event)" />
            <input name="title" [(ngModel)]="meta.title" placeholder="Title (optional)" />
            <input name="category" [(ngModel)]="meta.category" placeholder="Category (optional)" />
            <input name="tags" [(ngModel)]="meta.tags" placeholder="Tags, comma separated" />
            <button type="submit" [disabled]="!file() || busy()">{{ busy() ? 'Ingesting…' : 'Upload' }}</button>
          </form>
        }
        @if (message()) {
          <p class="notice">{{ message() }}</p>
        }
        <table class="grid">
          <thead><tr><th>Title</th><th>Category</th><th>Format</th><th>Status</th><th>Updated</th></tr></thead>
          <tbody>
            @for (d of docs(); track d.id) {
              <tr [class.selected]="d.id === selected()?.id">
                <td><a [routerLink]="['/documents', d.id]">{{ d.title }}</a></td>
                <td>{{ d.category }}</td>
                <td>{{ d.format }}</td>
                <td><span class="badge" [class]="'badge doc-' + d.status">{{ d.status }}</span></td>
                <td class="muted">{{ d.updated_at | date: 'short' }}</td>
              </tr>
            } @empty {
              <tr><td colspan="5" class="muted">No documents yet.</td></tr>
            }
          </tbody>
        </table>
      </section>

      @if (selected(); as d) {
        <aside class="card detail">
          <h3>{{ d.title }}</h3>
          <p class="muted small">
            {{ d.filename }} · {{ d.size_bytes / 1024 | number: '1.0-1' }} KB · {{ d.chunk_count }} chunks
            @if (d.page_count) { · {{ d.page_count }} pages } · uploaded by {{ d.uploaded_by }}
          </p>
          @if (d.error) {
            <p class="error">{{ d.error }}</p>
          }
          <h4>Summary</h4>
          <p>{{ d.summary || 'No summary (the model was unavailable at ingestion).' }}</p>
          @if (d.key_points.length) {
            <h4>Key points</h4>
            <ul>
              @for (k of d.key_points; track k) {
                <li>{{ k }}</li>
              }
            </ul>
          }
          @if (d.outline.length) {
            <h4>Outline</h4>
            <ol class="small">
              @for (o of d.outline; track $index) {
                <li>{{ o }}</li>
              }
            </ol>
          }
          @if (d.extracted_rule_codes.length) {
            <p class="small">Rules from this document: {{ d.extracted_rule_codes.join(', ') }}</p>
          }
          <div class="actions">
            <a [href]="api.downloadUrl(d.id)">Download original</a>
            @if (id.isAdmin()) {
              <button type="button" (click)="propose(d)" [disabled]="busy()">Extract rules</button>
              <button type="button" class="danger" (click)="remove(d)">Delete</button>
            }
          </div>

          @if (proposals().length) {
            <h4>Proposed rules (not saved yet)</h4>
            <ul class="proposals">
              @for (p of proposals(); track $index) {
                <li>
                  <label>
                    <input type="checkbox" [checked]="chosen().has($index)" (change)="toggle($index)" />
                    <strong>{{ p.title }}</strong>
                    <span class="badge" [class]="'badge sev-' + p.severity">{{ p.severity }}</span>
                    <span class="muted">{{ p.category }}</span>
                  </label>
                  <div class="small">{{ p.statement }}</div>
                </li>
              }
            </ul>
            <button type="button" (click)="approve(d)" [disabled]="!chosen().size">Add {{ chosen().size }} selected rule(s)</button>
          }
        </aside>
      }
    </div>
  `,
})
export class DocumentsPage implements OnInit {
  readonly id = inject(IdentityService);
  readonly api = inject(ApiService);
  private readonly router = inject(Router);
  readonly routeId = input<string | undefined>(undefined, { alias: 'id' });

  readonly docs = signal<DocumentRecord[]>([]);
  readonly selected = signal<DocumentRecord | null>(null);
  readonly file = signal<File | null>(null);
  readonly busy = signal(false);
  readonly message = signal('');
  readonly proposals = signal<RuleIn[]>([]);
  readonly chosen = signal<Set<number>>(new Set());
  meta = { title: '', category: '', tags: '' };

  constructor() {
    effect(() => {
      const rid = this.routeId();
      this.proposals.set([]);
      if (rid) this.api.document(rid).subscribe((d) => this.selected.set(d));
      else this.selected.set(null);
    });
  }

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.api.documents().subscribe((d) => this.docs.set(d));
  }

  pick(ev: Event): void {
    this.file.set((ev.target as HTMLInputElement).files?.[0] ?? null);
  }

  upload(): void {
    const f = this.file();
    if (!f) return;
    this.busy.set(true);
    this.message.set('');
    this.api.uploadDocument(f, this.meta).subscribe({
      next: (d) => {
        this.busy.set(false);
        this.message.set(d.id ? `Ingested "${d.title}" (${d.chunk_count} chunks).` : `Processing ${f.name} in the background.`);
        this.meta = { title: '', category: '', tags: '' };
        this.refresh();
        if (d.id) this.router.navigate(['/documents', d.id]);
      },
      error: (e) => {
        this.busy.set(false);
        this.message.set(`Upload failed: ${e.error?.detail ?? e.message}`);
      },
    });
  }

  remove(d: DocumentRecord): void {
    if (!confirm(`Delete "${d.title}"? Its passages leave the knowledge base.`)) return;
    this.api.deleteDocument(d.id).subscribe(() => {
      this.router.navigate(['/documents']);
      this.refresh();
    });
  }

  propose(d: DocumentRecord): void {
    this.busy.set(true);
    this.api.proposeRules(d.id).subscribe({
      next: (rules) => {
        this.busy.set(false);
        this.proposals.set(rules);
        this.chosen.set(new Set(rules.map((_, i) => i)));
      },
      error: (e) => {
        this.busy.set(false);
        this.message.set(`Extraction failed: ${e.error?.detail ?? e.message}`);
      },
    });
  }

  toggle(i: number): void {
    this.chosen.update((s) => {
      const n = new Set(s);
      n.has(i) ? n.delete(i) : n.add(i);
      return n;
    });
  }

  approve(d: DocumentRecord): void {
    const picked = this.proposals()
      .filter((_, i) => this.chosen().has(i))
      .map((r) => ({ ...r, source_document_id: d.id }));
    this.api.createRules(picked).subscribe((created) => {
      this.message.set(`Added ${created.map((r) => r.code).join(', ')}.`);
      this.proposals.set([]);
      this.api.document(d.id).subscribe((doc) => this.selected.set(doc));
    });
  }
}
