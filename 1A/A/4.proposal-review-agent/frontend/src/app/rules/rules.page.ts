import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { IdentityService } from '../core/identity';
import { Rule, RuleIn, RuleVersion, Severity } from '../core/models';

const EMPTY: RuleIn = { title: '', statement: '', severity: 'hard', category: '', rationale: '', exception_process: '' };

@Component({
  selector: 'app-rules-page',
  imports: [FormsModule, DatePipe],
  template: `
    <h2>Rules</h2>
    <form class="filters" (ngSubmit)="refresh()">
      <input name="q" [(ngModel)]="filter.q" placeholder="Search text or code" />
      <input name="category" [(ngModel)]="filter.category" placeholder="Category" />
      <select name="severity" [(ngModel)]="filter.severity">
        <option value="">Any severity</option>
        <option value="hard">Hard</option>
        <option value="flexible">Flexible</option>
      </select>
      <select name="status" [(ngModel)]="filter.status">
        <option value="active">Active</option>
        <option value="retired">Retired</option>
        <option value="">All</option>
      </select>
      <button type="submit">Filter</button>
      @if (id.isAdmin()) {
        <span class="spacer"></span>
        <button type="button" (click)="startCreate()">+ New rule</button>
        <label class="file">Import CSV/JSON <input type="file" accept=".csv,.json" (change)="import($event)" /></label>
      }
    </form>
    @if (message()) {
      <p class="notice">{{ message() }}</p>
    }

    @if (editing(); as e) {
      <form class="card rule-form" (ngSubmit)="save()">
        <strong>{{ editCode() ? 'Edit ' + editCode() : 'New rule' }}</strong>
        @if (!editCode()) {
          <input name="code" [(ngModel)]="e.code" placeholder="Code (optional, e.g. PRIV-010)" />
        }
        <input name="title" [(ngModel)]="e.title" placeholder="Title" required />
        <textarea name="statement" [(ngModel)]="e.statement" rows="3" placeholder="Statement: X must / must not…" required></textarea>
        <div class="row">
          <select name="severity" [(ngModel)]="e.severity">
            <option value="hard">Hard: no exceptions</option>
            <option value="flexible">Flexible: allowed with conditions</option>
          </select>
          <input name="category" [(ngModel)]="e.category" placeholder="Category" required />
        </div>
        <input name="rationale" [(ngModel)]="e.rationale" placeholder="Rationale" />
        @if (e.severity === 'flexible') {
          <input name="exception" [(ngModel)]="e.exception_process" placeholder="Exception process (who approves)" />
        }
        @if (editCode()) {
          <input name="note" [(ngModel)]="changeNote" placeholder="Change note (audit trail)" />
        }
        <div class="row">
          <button type="submit">Save</button>
          <button type="button" class="ghost" (click)="editing.set(null)">Cancel</button>
        </div>
      </form>
    }

    <table class="grid">
      <thead><tr><th>Code</th><th>Rule</th><th>Severity</th><th>Category</th><th>v</th><th></th></tr></thead>
      <tbody>
        @for (r of rules(); track r.code) {
          <tr>
            <td><strong>{{ r.code }}</strong></td>
            <td>
              <div>{{ r.title }}</div>
              <div class="small muted">{{ r.statement }}</div>
              @if (r.exception_process) {
                <div class="small">Exception: {{ r.exception_process }}</div>
              }
            </td>
            <td><span class="badge" [class]="'badge sev-' + r.severity">{{ r.severity }}</span></td>
            <td>{{ r.category }}</td>
            <td><button type="button" class="link" (click)="history(r)">{{ r.version }}</button></td>
            <td class="actions">
              @if (id.isAdmin() && r.status === 'active') {
                <button type="button" class="ghost" (click)="startEdit(r)">Edit</button>
                <button type="button" class="ghost danger" (click)="retire(r)">Retire</button>
              }
            </td>
          </tr>
          @if (versionsFor() === r.code) {
            <tr class="versions">
              <td></td>
              <td colspan="5">
                @for (v of versions(); track v.version) {
                  <div class="small">v{{ v.version }} · {{ v.changed_at | date: 'short' }} · {{ v.changed_by }} · {{ v.change_note }}</div>
                }
              </td>
            </tr>
          }
        } @empty {
          <tr><td colspan="6" class="muted">No rules match.</td></tr>
        }
      </tbody>
    </table>
  `,
})
export class RulesPage implements OnInit {
  readonly id = inject(IdentityService);
  private readonly api = inject(ApiService);

  readonly rules = signal<Rule[]>([]);
  readonly editing = signal<RuleIn | null>(null);
  readonly editCode = signal<string | null>(null);
  readonly versions = signal<RuleVersion[]>([]);
  readonly versionsFor = signal<string | null>(null);
  readonly message = signal('');
  filter: { q: string; category: string; severity: '' | Severity; status: string } = { q: '', category: '', severity: '', status: 'active' };
  changeNote = '';

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.api.rules(this.filter).subscribe((r) => this.rules.set(r));
  }

  startCreate(): void {
    this.editCode.set(null);
    this.editing.set({ ...EMPTY });
  }

  startEdit(r: Rule): void {
    this.editCode.set(r.code);
    this.changeNote = '';
    this.editing.set({
      title: r.title, statement: r.statement, severity: r.severity, category: r.category,
      rationale: r.rationale, exception_process: r.exception_process,
    });
  }

  save(): void {
    const e = this.editing();
    if (!e) return;
    const code = this.editCode();
    const req = code
      ? this.api.updateRule(code, { ...e, change_note: this.changeNote })
      : this.api.createRule({ ...e, code: e.code || null });
    req.subscribe({
      next: (r) => {
        this.message.set(`${code ? 'Updated' : 'Created'} ${r.code} (v${r.version}).`);
        this.editing.set(null);
        this.refresh();
      },
      error: (err) => this.message.set(`Save failed: ${JSON.stringify(err.error?.detail ?? err.message)}`),
    });
  }

  retire(r: Rule): void {
    const reason = prompt(`Retire ${r.code}? Reason:`);
    if (reason === null) return;
    this.api.retireRule(r.code, reason).subscribe(() => {
      this.message.set(`Retired ${r.code}.`);
      this.refresh();
    });
  }

  history(r: Rule): void {
    if (this.versionsFor() === r.code) {
      this.versionsFor.set(null);
      return;
    }
    this.api.ruleVersions(r.code).subscribe((v) => {
      this.versions.set(v);
      this.versionsFor.set(r.code);
    });
  }

  import(ev: Event): void {
    const el = ev.target as HTMLInputElement;
    const f = el.files?.[0];
    el.value = '';
    if (!f) return;
    this.api.importRules(f).subscribe({
      next: (rules) => {
        this.message.set(`Imported ${rules.length} rule(s).`);
        this.refresh();
      },
      error: (err) => this.message.set(`Import failed: ${err.error?.detail ?? err.message}`),
    });
  }
}
