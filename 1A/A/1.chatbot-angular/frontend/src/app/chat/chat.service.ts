// The only file that knows the backend URL and wire format.
import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ChatResponse {
  session_id: string;
  reply: string;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly http = inject(HttpClient);

  send(message: string, sessionId: string | null): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${environment.apiUrl}/api/v1/chat`, {
      message,
      session_id: sessionId,
    });
  }
}
