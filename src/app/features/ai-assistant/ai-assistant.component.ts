import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';

export interface Incident {
  id: string;
  incId: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  timeAgo: string;
  stage?: string;
  description?: string;
}

export interface Investigation {
  id: string;
  title: string;
  timeAgo: string;
  status: 'Resolved' | 'Closed' | 'Assigned';
  avatarColor?: string;
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
}

@Component({
  selector: 'app-ai-assistant',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './ai-assistant.component.html',
  styleUrls: ['./ai-assistant.component.scss']
})
export class AiAssistantComponent {
  private api = inject(ApiService);
  
  userPrompt = signal<string>('');
  isGenerating = signal<boolean>(false);
  chatHistory = signal<ChatMessage[]>([]);

  liveIncidents = signal<Incident[]>([
    {
      id: '1',
      incId: 'INC-18492',
      severity: 'HIGH',
      title: 'Title',
      description: 'Description',
      timeAgo: '6 mins ago'
    },
    {
      id: '2',
      incId: 'INC-18487',
      severity: 'MEDIUM',
      title: 'Authentication latency',
      stage: 'Listener Agent',
      timeAgo: '12 mins ago'
    },
    {
      id: '3',
      incId: 'INC-18481',
      severity: 'LOW',
      title: 'Inventory sync delay',
      stage: 'Self-Healing running',
      timeAgo: '45 mins ago'
    }
  ]);

  recentInvestigations = signal<Investigation[]>([
    { id: '1', title: 'Title', timeAgo: '2h ago', status: 'Resolved', avatarColor: '#e8f5e9' },
    { id: '2', title: 'Title', timeAgo: '5h ago', status: 'Closed', avatarColor: '#e0e0e0' },
    { id: '3', title: 'Title', timeAgo: '1d ago', status: 'Assigned', avatarColor: '#fbe9e7' }
  ]);

  suggestions = signal<string[]>([
    'Investigate latest incident',
    'Explain root cause',
    'Show live incidents',
    'Analyze deployment',
    'Search similar incidents',
    'Generate postmortem',
    'Execute approved playbook'
  ]);

  clearWindow() {
    this.userPrompt.set('');
    this.chatHistory.set([]);
  }

  setSuggestion(suggestion: string) {
    this.userPrompt.set(suggestion);
    this.onSend();
  }

  onSend() {
    const prompt = this.userPrompt().trim();
    if (!prompt || this.isGenerating()) return;

    // Add user message to UI
    const currentHistory = this.chatHistory();
    this.chatHistory.set([...currentHistory, { role: 'user', text: prompt }]);
    this.userPrompt.set('');
    this.isGenerating.set(true);

    // Call API with history (excluding the new message we just added so the backend treats it as the new prompt)
    this.api.chatGemini(prompt, currentHistory).subscribe({
      next: (res) => {
        this.chatHistory.update(history => [...history, { role: 'model', text: res.response }]);
        this.isGenerating.set(false);
      },
      error: (err) => {
        console.error('Gemini error:', err);
        this.chatHistory.update(history => [...history, { role: 'model', text: 'Error connecting to Vertex AI. Please check your network and ADC credentials.' }]);
        this.isGenerating.set(false);
      }
    });
  }
}