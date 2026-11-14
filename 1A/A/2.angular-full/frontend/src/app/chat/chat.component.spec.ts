import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';
import { ChatComponent } from './chat.component';
import { ChatService, StreamEvent } from './chat.service';

describe('ChatComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('json mode: posts the message and renders reply + trace', () => {
    const cmp = TestBed.createComponent(ChatComponent).componentInstance;
    const http = TestBed.inject(HttpTestingController);
    cmp.streaming.set(false);

    cmp.input = 'hi';
    cmp.send();
    const req = http.expectOne((r) => r.url.endsWith('/api/v1/chat'));
    expect(req.request.body).toEqual({ message: 'hi', session_id: null });
    req.flush({
      session_id: 's1',
      reply: 'hello',
      events: [{ type: 'tool_call', author: 'orchestrator', name: 'calculate', args: { expression: '1+1' } }],
    });

    expect(cmp.sessionId()).toBe('s1');
    const last = cmp.messages()[1];
    expect(last.text).toBe('hello');
    expect(cmp.label(last.events[0])).toContain('calculate');
    http.verify();
  });

  it('stream mode: accumulates deltas, collects trace, takes final reply from done', () => {
    const svc = TestBed.inject(ChatService);
    const events: StreamEvent[] = [
      { type: 'tool_call', author: 'orchestrator', name: 'get_current_time', args: { timezone: 'UTC' } },
      { type: 'delta', text: 'It is ' },
      { type: 'delta', text: 'noon.' },
      { type: 'done', session_id: 's2', reply: 'It is noon.' },
    ];
    vi.spyOn(svc, 'stream').mockReturnValue(of(...events));
    const cmp = TestBed.createComponent(ChatComponent).componentInstance;

    cmp.input = 'time?';
    cmp.send();

    expect(svc.stream).toHaveBeenCalledWith('time?', null);
    expect(cmp.sessionId()).toBe('s2');
    expect(cmp.messages()[1].text).toBe('It is noon.');
    expect(cmp.messages()[1].events.length).toBe(1);
    expect(cmp.busy()).toBe(false);
  });
});
