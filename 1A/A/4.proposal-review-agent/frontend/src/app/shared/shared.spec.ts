import { TestBed } from '@angular/core/testing';
import { Verdict } from '../core/models';
import { MarkdownPipe } from './markdown.pipe';
import { VerdictCardComponent } from './verdict-card.component';

const VERDICT: Verdict = {
  assessment_id: 'a1',
  verdict: 'NON_COMPLIANT',
  summary: 'Blocked by the children rule.',
  blocking: ['PRIV-003: Verifiable parental consent for children under 13'],
  conditions: ['MKT-002: Keep test results (exception: Legal)'],
  missing_information: [],
  findings: [
    { rule_code: 'PRIV-003', rule_title: 'Parental consent', severity: 'hard', status: 'violated', reasoning: 'No consent.', evidence: [{ source: 'rule PRIV-003', quote: 'must obtain' }], remediation: 'Add consent', exception_process: '' },
    { rule_code: 'FIN-001', rule_title: 'CFO approval', severity: 'hard', status: 'not_applicable', reasoning: '', evidence: [], remediation: '', exception_process: '' },
  ],
  rules_considered: 14,
  disclaimer: 'Decision support.',
};

describe('MarkdownPipe', () => {
  const md = new MarkdownPipe();
  it('escapes html and renders the supported subset', () => {
    expect(md.transform('<b>x</b>')).toBe('<p>&lt;b&gt;x&lt;/b&gt;</p>');
    expect(md.transform('**NON-COMPLIANT** see `PRIV-003`')).toBe('<p><strong>NON-COMPLIANT</strong> see <code>PRIV-003</code></p>');
    expect(md.transform('- a\n- b\ntext')).toBe('<ul><li>a</li><li>b</li></ul><p>text</p>');
  });
});

describe('VerdictCardComponent', () => {
  it('shows the label, blocking rules, and hides not-applicable findings', async () => {
    await TestBed.configureTestingModule({ imports: [VerdictCardComponent] }).compileComponents();
    const f = TestBed.createComponent(VerdictCardComponent);
    f.componentRef.setInput('verdict', VERDICT);
    f.componentInstance.open.set(true);
    await f.whenStable();
    const el = f.nativeElement as HTMLElement;
    expect(el.querySelector('.verdict-label')?.textContent).toContain('Non-compliant');
    expect(el.textContent).toContain('PRIV-003: Verifiable parental consent');
    expect(el.querySelectorAll('.findings tbody tr').length).toBe(1);
    expect(el.querySelector('blockquote')?.textContent).toContain('must obtain');
  });
});
