import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ChatComponent } from './chat.component';

describe('ChatComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('posts the message and keeps the session id', async () => {
    const fixture = TestBed.createComponent(ChatComponent);
    const cmp = fixture.componentInstance;
    const http = TestBed.inject(HttpTestingController);

    cmp.input = 'hi';
    cmp.send();
    const req = http.expectOne((r) => r.url.endsWith('/api/v1/chat'));
    expect(req.request.body).toEqual({ message: 'hi', session_id: null });
    req.flush({ session_id: 's1', reply: 'hello' });

    expect(cmp.sessionId()).toBe('s1');
    expect(cmp.messages().map((m) => m.text)).toEqual(['hi', 'hello']);

    cmp.input = 'again';
    cmp.send();
    expect(http.expectOne(() => true).request.body.session_id).toBe('s1');
    http.verify();
  });
});
