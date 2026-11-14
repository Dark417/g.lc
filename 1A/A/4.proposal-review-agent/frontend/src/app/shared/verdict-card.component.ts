import { Component, computed, input, signal } from '@angular/core';
import { Finding, Verdict } from '../core/models';

const LABELS: Record<string, string> = {
  COMPLIANT: 'Compliant',
  CONDITIONALLY_COMPLIANT: 'Conditionally compliant',
  NON_COMPLIANT: 'Non-compliant',
  NEEDS_MORE_INFO: 'Needs more info',
};

@Component({
  selector: 'app-verdict-card',
  template: `
    @let v = verdict();
    <section class="verdict" [class]="'verdict v-' + v.verdict">
      <header>
        <span class="verdict-label">{{ label() }}</span>
        <span class="muted">{{ v.rules_considered }} rules considered</span>
      </header>
      @if (v.summary) {
        <p>{{ v.summary }}</p>
      }
      @if (v.blocking.length) {
        <h4>Blocking (hard rules)</h4>
        <ul>
          @for (b of v.blocking; track b) {
            <li>{{ b }}</li>
          }
        </ul>
      }
      @if (v.conditions.length) {
        <h4>Conditions (flexible rules)</h4>
        <ul>
          @for (c of v.conditions; track c) {
            <li>{{ c }}</li>
          }
        </ul>
      }
      @if (v.missing_information.length) {
        <h4>Missing information</h4>
        <ul>
          @for (m of v.missing_information; track m) {
            <li>{{ m }}</li>
          }
        </ul>
      }
      <button class="link" type="button" (click)="open.set(!open())">
        {{ open() ? 'Hide' : 'Show' }} findings ({{ relevant().length }} relevant)
      </button>
      @if (open()) {
        <table class="findings">
          <thead>
            <tr><th>Rule</th><th>Severity</th><th>Status</th><th>Reasoning and evidence</th></tr>
          </thead>
          <tbody>
            @for (f of relevant(); track f.rule_code) {
              <tr>
                <td><strong>{{ f.rule_code }}</strong><br /><span class="muted">{{ f.rule_title }}</span></td>
                <td><span class="badge" [class]="'badge sev-' + f.severity">{{ f.severity }}</span></td>
                <td><span class="badge" [class]="'badge st-' + f.status">{{ f.status }}</span></td>
                <td>
                  {{ f.reasoning }}
                  @for (e of f.evidence; track $index) {
                    <blockquote>“{{ e.quote }}” <cite>{{ e.source }}</cite></blockquote>
                  }
                  @if (f.remediation) {
                    <div class="muted">Remediation: {{ f.remediation }}</div>
                  }
                  @if (f.exception_process && f.status !== 'satisfied') {
                    <div class="muted">Exception: {{ f.exception_process }}</div>
                  }
                </td>
              </tr>
            }
          </tbody>
        </table>
      }
      <p class="muted small">{{ v.disclaimer }}</p>
    </section>
  `,
})
export class VerdictCardComponent {
  readonly verdict = input.required<Verdict>();
  readonly open = signal(false);
  readonly label = computed(() => LABELS[this.verdict().verdict] ?? this.verdict().verdict);
  readonly relevant = computed<Finding[]>(() =>
    this.verdict().findings.filter((f) => f.status !== 'not_applicable'),
  );
}
