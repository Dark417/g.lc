import { HttpInterceptorFn } from '@angular/common/http';
import { Injectable, computed, signal } from '@angular/core';
import { Me } from './models';

const KEY = 'proposal-review.dev-user';

function read(): string {
  try {
    return localStorage.getItem(KEY) ?? '';
  } catch {
    return '';
  }
}

/**
 * Who the portal acts as.
 * - Local (AUTH_MODE=dev): the backend trusts X-User-Email, so the header lets you switch users.
 * - GCP (AUTH_MODE=iap): IAP signs the request; the backend ignores this header.
 */
@Injectable({ providedIn: 'root' })
export class IdentityService {
  readonly devUser = signal(read());
  readonly me = signal<Me | null>(null);
  readonly isAdmin = computed(() => this.me()?.role === 'admin');

  setDevUser(email: string): void {
    const v = email.trim().toLowerCase();
    this.devUser.set(v);
    try {
      v ? localStorage.setItem(KEY, v) : localStorage.removeItem(KEY);
    } catch {
      /* storage unavailable: header only lives for this tab */
    }
  }
}

// Functional interceptor: reads the signal at request time.
let current: IdentityService | null = null;
export function bindIdentity(svc: IdentityService): void {
  current = svc;
}

export const identityInterceptor: HttpInterceptorFn = (req, next) => {
  const user = current?.devUser();
  return next(user ? req.clone({ setHeaders: { 'X-User-Email': user } }) : req);
};

export function identityHeaders(): Record<string, string> {
  const user = current?.devUser();
  return user ? { 'X-User-Email': user } : {};
}
