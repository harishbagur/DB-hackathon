import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {
  // Signal state for dynamic reactivity
  kpis = signal([
    { title: 'Security Health Score', value: '92%', change: '8% vs yesterday', isPositive: true, type: 'health' },
    { title: 'Open Incidents', value: '12', change: '2 new', isPositive: false, type: 'incidents' },
    { title: 'High Risk Alerts', value: '4', change: '1 new', isPositive: false, type: 'alerts' },
    { title: 'Automated Resolved', value: '36', change: '12 today', isPositive: true, type: 'resolved' },
    { title: 'Avg. Resolution Time', value: '4m 22s', change: '1m vs yesterday', isPositive: true, type: 'time' },
    { title: 'DORA Compliance', value: '96%', change: 'Compliant', isPositive: true, type: 'dora' }
  ]);

  incidents = signal([
    { id: 'INC548239', title: 'VPN Authentication Failure', priority: 'Critical', status: 'Investigating', time: '09:15 AM' },
    { id: 'INC548240', title: 'Windows Patch Failure', priority: 'High', status: 'Investigating', time: '08:42 AM' },
    { id: 'INC548241', title: 'Email Service Down', priority: 'High', status: 'Resolved', time: 'Yesterday' },
    { id: 'INC548242', title: 'Database Connection Issue', priority: 'Medium', status: 'Investigating', time: 'Yesterday' },
    { id: 'INC548243', title: 'Network Latency High', priority: 'Medium', status: 'Resolved', time: '2 days ago' }
  ]);

  agents = signal([
    { name: 'Incident Agent', task: 'Analyzing incident', progress: 100, isDone: true },
    { name: 'Knowledge Agent', task: 'Searching knowledge base', progress: 100, isDone: true },
    { name: 'Windows Agent', task: 'Checking system services', progress: 65, isDone: false },
    { name: 'Network Agent', task: 'Analyzing network logs', progress: 100, isDone: true },
    { name: 'Vulnerability Agent', task: 'Checking known vulnerabilities', progress: 100, isDone: true }
  ]);
}