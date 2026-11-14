// The only module that knows backend URLs and the wire format.
import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { identityHeaders } from './identity';
import {
  Attachment,
  ChatMessage,
  Conversation,
  DocumentRecord,
  Me,
  Rule,
  RuleIn,
  RuleVersion,
  StreamEvent,
  Verdict,
} from './models';

const API = `${environment.apiUrl}/api/v1`;

function params(obj: Record<string, string | undefined>): HttpParams {
  let p = new HttpParams();
  for (const [k, v] of Object.entries(obj)) if (v) p = p.set(k, v);
  return p;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);

  me(): Observable<Me> {
    return this.http.get<Me>(`${API}/me`);
  }

  // ---- rules
  rules(filter: { category?: string; severity?: string; q?: string; status?: string } = {}): Observable<Rule[]> {
    return this.http.get<Rule[]>(`${API}/rules`, { params: params(filter) });
  }
  ruleVersions(code: string): Observable<RuleVersion[]> {
    return this.http.get<RuleVersion[]>(`${API}/rules/${code}/versions`);
  }
  createRule(rule: RuleIn): Observable<Rule> {
    return this.http.post<Rule>(`${API}/rules`, rule);
  }
  createRules(rules: RuleIn[]): Observable<Rule[]> {
    return this.http.post<Rule[]>(`${API}/rules/bulk`, rules);
  }
  updateRule(code: string, patch: Partial<RuleIn> & { change_note?: string }): Observable<Rule> {
    return this.http.patch<Rule>(`${API}/rules/${code}`, patch);
  }
  retireRule(code: string, reason: string): Observable<Rule> {
    return this.http.delete<Rule>(`${API}/rules/${code}`, { params: params({ reason }) });
  }
  importRules(file: File): Observable<Rule[]> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<Rule[]>(`${API}/rules/import`, form);
  }

  // ---- documents
  documents(category?: string): Observable<DocumentRecord[]> {
    return this.http.get<DocumentRecord[]>(`${API}/documents`, { params: params({ category }) });
  }
  document(id: string): Observable<DocumentRecord> {
    return this.http.get<DocumentRecord>(`${API}/documents/${id}`);
  }
  uploadDocument(file: File, meta: { title?: string; category?: string; tags?: string }): Observable<DocumentRecord> {
    const form = new FormData();
    form.append('file', file);
    for (const [k, v] of Object.entries(meta)) if (v) form.append(k, v);
    return this.http.post<DocumentRecord>(`${API}/documents`, form);
  }
  deleteDocument(id: string): Observable<void> {
    return this.http.delete<void>(`${API}/documents/${id}`);
  }
  proposeRules(id: string): Observable<RuleIn[]> {
    return this.http.post<RuleIn[]>(`${API}/documents/${id}/propose-rules`, {});
  }
  downloadUrl(id: string): string {
    return `${API}/documents/${id}/download`;
  }

  // ---- assess
  assess(proposal: string, context = ''): Observable<Verdict> {
    return this.http.post<Verdict>(`${API}/assess`, { proposal, context });
  }

  // ---- conversations
  conversations(): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(`${API}/conversations`);
  }
  conversation(id: string): Observable<{ id: string; title: string; messages: ChatMessage[] }> {
    return this.http.get<{ id: string; title: string; messages: ChatMessage[] }>(`${API}/conversations/${id}`);
  }
  deleteConversation(id: string): Observable<void> {
    return this.http.delete<void>(`${API}/conversations/${id}`);
  }

  /**
   * Server-Sent Events over fetch (HttpClient can't consume a streaming body).
   * Parses `data: <json>` frames separated by a blank line.
   */
  stream(message: string, sessionId: string | null, attachments: Attachment[] = []): Observable<StreamEvent> {
    return new Observable<StreamEvent>((sub) => {
      const ctrl = new AbortController();
      (async () => {
        try {
          const res = await fetch(`${API}/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...identityHeaders() },
            body: JSON.stringify({ message, session_id: sessionId, attachments }),
            signal: ctrl.signal,
          });
          if (!res.ok || !res.body) throw new Error(`backend ${res.status}: ${await res.text()}`);
          const reader = res.body.getReader();
          const decoder = new TextDecoder();
          let buf = '';
          for (;;) {
            const { value, done } = await reader.read();
            if (done) break;
            buf += decoder.decode(value, { stream: true });
            let i: number;
            while ((i = buf.indexOf('\n\n')) >= 0) {
              const line = buf.slice(0, i).split('\n').find((l) => l.startsWith('data: '));
              buf = buf.slice(i + 2);
              if (line) sub.next(JSON.parse(line.slice(6)) as StreamEvent);
            }
          }
          sub.complete();
        } catch (e) {
          if (!ctrl.signal.aborted) sub.error(e);
        }
      })();
      return () => ctrl.abort();
    });
  }
}

export function fileToAttachment(file: File): Promise<Attachment> {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onerror = () => reject(r.error);
    r.onload = () => {
      const url = r.result as string; // data:<mime>;base64,<data>
      resolve({
        filename: file.name,
        mime_type: file.type || 'application/octet-stream',
        data_base64: url.slice(url.indexOf(',') + 1),
      });
    };
    r.readAsDataURL(file);
  });
}
