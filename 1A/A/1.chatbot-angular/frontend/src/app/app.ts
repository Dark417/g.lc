import { Component } from '@angular/core';
import { ChatComponent } from './chat/chat.component';

@Component({
  selector: 'app-root',
  imports: [ChatComponent],
  template: `
    <main>
      <h1>Chatbot</h1>
      <app-chat />
    </main>
  `,
})
export class App {}
