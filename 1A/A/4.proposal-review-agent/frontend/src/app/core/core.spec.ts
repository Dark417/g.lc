import { TestBed } from '@angular/core/testing';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ApiService } from './api.service';
import { IdentityService, bindIdentity, identityInterceptor } from './identity';

describe('ApiService + identity interceptor', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(withInterceptors([identityInterceptor])), provideHttpClientTesting()],
    });
  });

  it('adds X-User-Email only when a dev identity is set, and passes filters', () => {
    const id = TestBed.inject(IdentityService);
    bindIdentity(id);
    const api = TestBed.inject(ApiService);
    const http = TestBed.inject(HttpTestingController);

    id.setDevUser('');
    api.me().subscribe();
    expect(http.expectOne((r) => r.url.endsWith('/api/v1/me')).request.headers.has('X-User-Email')).toBe(false);

    id.setDevUser('Admin@Example.com');
    api.rules({ severity: 'hard', q: '' }).subscribe();
    const req = http.expectOne((r) => r.url.endsWith('/api/v1/rules'));
    expect(req.request.headers.get('X-User-Email')).toBe('admin@example.com');
    expect(req.request.params.get('severity')).toBe('hard');
    expect(req.request.params.has('q')).toBe(false);
    http.verify();
    id.setDevUser('');
  });

  it('isAdmin follows /me', () => {
    const id = TestBed.inject(IdentityService);
    id.me.set({ user_id: 'a', role: 'admin', kind: 'human', adk_web: false, auth_mode: 'dev' });
    expect(id.isAdmin()).toBe(true);
    id.me.set({ user_id: 'b', role: 'user', kind: 'human', adk_web: false, auth_mode: 'iap' });
    expect(id.isAdmin()).toBe(false);
  });
});
