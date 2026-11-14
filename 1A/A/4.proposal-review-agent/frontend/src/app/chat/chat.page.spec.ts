import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter, Router } from '@angular/router';
import { of } from 'rxjs';
import { ApiService } from '../core/api.service';
import { StreamEvent, Verdict } from '../core/models';
import { ChatPage } from './chat.page';

const verdict = { assessment_id: 'a1', verdict: 'NON_COMPLIANT', findings: [], blocking: ['FIN-001: CFO'], conditions: [], missing_information: [], summary: '', rules_considered: 3, disclaimer: '' } as Verdict;

describe('ChatPage', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatPage],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();
  });

  it('streams a turn: session id, trace, verdict card, final reply', async () => {
    const api = TestBed.inject(ApiService);
    const events: StreamEvent[] = [
      { type: 'session', session_id: 's1' },
      { type: 'tool_call', author: 'compliance_agent', name: 'assess_proposal', args: { proposal: '60% off' } },
      { type: 'verdict', verdict },
      { type: 'delta', text: '**NON-' },
      { type: 'delta', text: 'COMPLIANT**' },
      { type: 'done', session_id: 's1', reply: '**NON-COMPLIANT** FIN-001 needs CFO approval.' },
    ];
    vi.spyOn(api, 'stream').mockReturnValue(of(...events));
    vi.spyOn(api, 'conversations').mockReturnValue(of([{ id: 's1', title: '60% off?', updated_at: 1 }]));
    const nav = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);

    const fixture = TestBed.createComponent(ChatPage);
    const page = fixture.componentInstance;
    await fixture.whenStable(); // page initialised (route effects ran) before the user types
    page.input = '60% off tomorrow?';
    await page.send();
    await fixture.whenStable();

    expect(api.stream).toHaveBeenCalledWith('60% off tomorrow?', null, []);
    expect(page.sessionId()).toBe('s1');
    expect(nav).toHaveBeenCalledWith(['/chat'], { queryParams: { c: 's1' }, replaceUrl: true });
    const [user, assistant] = page.messages();
    expect(user.text).toBe('60% off tomorrow?');
    expect(assistant.verdicts[0].verdict).toBe('NON_COMPLIANT');
    expect(assistant.trace?.[0].name).toBe('assess_proposal');
    expect(assistant.text).toContain('CFO approval');
    expect(page.busy()).toBe(false);
    expect(page.conversations()[0].title).toBe('60% off?');

    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).querySelector('app-verdict-card')).toBeTruthy();
  });
});
