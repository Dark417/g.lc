import { Routes } from '@angular/router';
import { ChatPage } from './chat/chat.page';
import { DocumentsPage } from './documents/documents.page';
import { RulesPage } from './rules/rules.page';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'chat' },
  // One route with ?c=<conversation id>: a separate 'chat/:id' route would destroy the page
  // (and its open stream) when a new conversation gets its id.
  { path: 'chat', component: ChatPage },
  { path: 'documents', component: DocumentsPage },
  { path: 'documents/:id', component: DocumentsPage },
  { path: 'rules', component: RulesPage },
  { path: '**', redirectTo: 'chat' },
];
