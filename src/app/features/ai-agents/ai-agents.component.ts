import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'Active' | 'Inactive';
  iconType: 'green-shield' | 'blue-shield';
}

@Component({
  selector: 'app-ai-agents',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './ai-agents.component.html',
  styleUrls: ['./ai-agents.component.scss']
})
export class AiAgentsComponent {
  agents = signal<Agent[]>([
    {
      id: '1',
      name: 'Incident Agent',
      description: 'Analyzes incidents and suggests solutions',
      status: 'Active',
      iconType: 'green-shield'
    },
    {
      id: '2',
      name: 'Knowledge Agent',
      description: 'Searches and recommends knowledge articles',
      status: 'Active',
      iconType: 'blue-shield'
    },
    {
      id: '3',
      name: 'Windows Agent',
      description: 'Monitors and resolves Windows related issues',
      status: 'Active',
      iconType: 'blue-shield'
    },
    {
      id: '4',
      name: 'Network Agent',
      description: 'Analyzes network logs and performance',
      status: 'Active',
      iconType: 'blue-shield'
    },
    {
      id: '5',
      name: 'Vulnerability Agent',
      description: 'Checks vulnerabilities and suggests fixes',
      status: 'Active',
      iconType: 'blue-shield'
    },
    {
      id: '6',
      name: 'Compliance Agent',
      description: 'Monitors compliance and regulatory controls',
      status: 'Active',
      iconType: 'blue-shield'
    }
  ]);

  onAddAgent() {
    console.log('Add Agent clicked');
  }
}