import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService, ChatResponse } from '../../services/api.service';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  confidence?: number;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule,
    MatFormFieldModule, 
    MatInputModule, 
    MatButtonModule, 
    MatSelectModule, 
    MatIconModule,
    MatChipsModule,
    MatTooltipModule
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent {
  @Input() hasDocuments = false;
  
  messages: Message[] = [];
  userMessage = '';
  selectedModel = 'openai';
  isLoading = false;
  sessionId = 'default';

  models = [
    { value: 'openai', label: 'OpenAI GPT-4' },
    { value: 'gemini', label: 'Google Gemini' },
    { value: 'anthropic', label: 'Anthropic Claude' }
  ];

  constructor(private apiService: ApiService) {}

  sendMessage() {
    if (!this.userMessage.trim() || this.isLoading) {
      return;
    }

    if (!this.hasDocuments) {
      this.messages.push({
        role: 'assistant',
        content: 'Please upload at least one document before chatting.'
      });
      return;
    }

    const message = this.userMessage.trim();
    this.messages.push({ role: 'user', content: message });
    this.userMessage = '';
    this.isLoading = true;

    this.apiService.chat({
      message,
      model: this.selectedModel,
      session_id: this.sessionId
    }).subscribe({
      next: (response: ChatResponse) => {
        this.messages.push({
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          confidence: response.confidence
        });
        this.isLoading = false;
        setTimeout(() => this.scrollToBottom(), 100);
      },
      error: (error) => {
        this.messages.push({
          role: 'assistant',
          content: `Error: ${error.error?.detail || error.message}`
        });
        this.isLoading = false;
      }
    });

    setTimeout(() => this.scrollToBottom(), 100);
  }

  resetChat() {
    this.apiService.resetSession(this.sessionId).subscribe({
      next: () => {
        this.messages = [];
        this.sessionId = 'session_' + Date.now();
      }
    });
  }

  scrollToBottom() {
    const chatContainer = document.querySelector('.messages-container');
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
}
