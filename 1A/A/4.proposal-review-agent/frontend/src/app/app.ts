import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { environment } from '../environments/environment';
import { ApiService } from './core/api.service';
import { IdentityService, bindIdentity } from './core/identity';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, FormsModule],
  template: `
    <header class="topbar">
      <strong class="brand">Proposal Review</strong>
      <nav>
        <a routerLink="/chat" routerLinkActive="active">Chat</a>
        <a routerLink="/documents" routerLinkActive="active">Documents</a>
        <a routerLink="/rules" routerLinkActive="active">Rules</a>
        @if (id.me()?.adk_web) {
          <a [href]="adkWebUrl" target="_blank" rel="noopener" title="ADK developer UI">Dev UI ↗</a>
        }
      </nav>
      <span class="spacer"></span>
      @if (id.me(); as me) {
        @if (me.auth_mode === 'dev') {
          <form class="whoami" (ngSubmit)="switchUser()">
            <input name="email" [(ngModel)]="email" placeholder="user@example.com" aria-label="Act as" />
            <button type="submit" class="ghost">Switch</button>
          </form>
        } @else {
          <span>{{ me.user_id }}</span>
        }
        <span class="badge" [class.badge-admin]="me.role === 'admin'">{{ me.role }}</span>
      } @else if (error()) {
        <span class="error">{{ error() }}</span>
      }
    </header>
    <main class="page">
      @if (id.me()) {
        <router-outlet />
      }
    </main>
  `,
})
export class App implements OnInit {
  readonly id = inject(IdentityService);
  private readonly api = inject(ApiService);
  readonly adkWebUrl = environment.adkWebUrl;
  readonly error = signal('');
  email = this.id.devUser();

  constructor() {
    bindIdentity(this.id);
  }

  ngOnInit(): void {
    this.loadMe();
  }

  switchUser(): void {
    this.id.setDevUser(this.email);
    this.id.me.set(null); // re-render pages for the new identity
    this.loadMe();
  }

  private loadMe(): void {
    this.api.me().subscribe({
      next: (me) => {
        this.id.me.set(me);
        this.email = me.user_id;
        this.error.set('');
      },
      error: (e) => this.error.set(`backend unreachable (${e.status ?? e.message})`),
    });
  }
}
