import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../core/services/api.service';
import { IncidentResponse, AgentResponse, ArticleResponse, ExecutiveMetricsResponse, EscalationResponse } from '../../core/models/api.models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  private api = inject(ApiService);

  // ─── Loading states ──────────────────────────────────────
  loading = signal(true);

  // ─── KPI Cards (computed from live data) ─────────────────
  kpis = signal([
    { title: 'Security Health Score', value: '92%', change: '8% vs yesterday', isPositive: true, type: 'health' },
    { title: 'Open Incidents', value: '12', change: '2 new', isPositive: false, type: 'incidents' },
    { title: 'High Risk Alerts', value: '4', change: '1 new', isPositive: false, type: 'alerts' },
    { title: 'Automated Resolved', value: '36', change: '12 today', isPositive: true, type: 'resolved' },
    { title: 'Avg. Resolution Time', value: '4m 22s', change: '1m vs yesterday', isPositive: true, type: 'time' },
    { title: 'DORA Compliance', value: '96%', change: 'Compliant', isPositive: true, type: 'dora' }
  ]);

  // ─── Recent Incidents ────────────────────────────────────
  incidents = signal<{ id: string; title: string; priority: string; status: string; time: string }[]>([
    { id: 'INC548239', title: 'VPN Authentication Failure', priority: 'Critical', status: 'Investigating', time: '09:15 AM' },
    { id: 'INC548240', title: 'Windows Patch Failure', priority: 'High', status: 'Investigating', time: '08:42 AM' },
    { id: 'INC548241', title: 'Email Service Down', priority: 'High', status: 'Resolved', time: 'Yesterday' },
    { id: 'INC548242', title: 'Database Connection Issue', priority: 'Medium', status: 'Investigating', time: 'Yesterday' },
    { id: 'INC548243', title: 'Network Latency High', priority: 'Medium', status: 'Resolved', time: '2 days ago' }
  ]);

  // ─── AI Multi-Agent Investigation ────────────────────────
  agents = signal<{ name: string; task: string; progress: number; isDone: boolean }[]>([
    { name: 'Incident Agent', task: 'Analyzing incident', progress: 100, isDone: true },
    { name: 'Knowledge Agent', task: 'Searching knowledge base', progress: 100, isDone: true },
    { name: 'Windows Agent', task: 'Checking system services', progress: 65, isDone: false },
    { name: 'Network Agent', task: 'Analyzing network logs', progress: 100, isDone: true },
    { name: 'Vulnerability Agent', task: 'Checking known vulnerabilities', progress: 100, isDone: true }
  ]);

  // ─── Knowledge Base ──────────────────────────────────────
  knowledgeArticles = signal<{ id: string; title: string; helpful: number }[]>([
    { id: 'KB-12451', title: 'VPN connection failure after patch', helpful: 98 },
    { id: 'KB-32910', title: 'VPN authentication issues', helpful: 97 }
  ]);

  // ─── Escalation Queue ────────────────────────────────────
  escalations = signal<{ id: string; incident: string; team: string; priority: string; eta: string }[]>([
    { id: 'ESC1001', incident: 'INC548239', team: 'Windows Ops', priority: 'Critical', eta: '5 mins' },
    { id: 'ESC1002', incident: 'INC548240', team: 'Network Team', priority: 'High', eta: '15 mins' }
  ]);

  // ─── Executive Overview ──────────────────────────────────
  execMetrics = signal<{
    automatedResolution: string; manualEscalation: string;
    avgResolutionTime: string; criticalIncidents: string;
  }>({
    automatedResolution: '87%', manualEscalation: '13%',
    avgResolutionTime: '4m 22s', criticalIncidents: '5'
  });

  ngOnInit(): void {
    this.fetchIncidents();
    this.fetchAgents();
    this.fetchKnowledgeArticles();
    this.fetchExecutiveMetrics();
    this.fetchDoraScores();
  }

  private fetchIncidents(): void {
    this.api.getIncidents().subscribe({
      next: (data: IncidentResponse[]) => {
        const mapped = data.map(inc => ({
          id: inc.incident_number,
          title: inc.title,
          priority: inc.priority,
          status: inc.status,
          time: inc.created_at ? this.formatTime(inc.created_at) : 'Unknown'
        }));
        if (mapped.length) this.incidents.set(mapped);

        // Update KPIs from live incident data
        const open = data.filter(i => i.status !== 'Resolved' && i.status !== 'Closed').length;
        const critical = data.filter(i => i.priority === 'Critical' || i.priority === 'High').length;
        this.updateKpi('incidents', String(open), open > 10 ? `${open} open` : `${open} open`);
        this.updateKpi('alerts', String(critical), `${critical} high/critical`);
      },
      error: () => {
        console.log('[Dashboard] Backend unavailable — using mock incident data');
      }
    });
  }

  private fetchAgents(): void {
    this.api.getAgents().subscribe({
      next: (data: AgentResponse[]) => {
        const mapped = data.map(a => ({
          name: a.agent_name,
          task: this.agentTaskLabel(a),
          progress: a.confidence_score ?? 0,
          isDone: a.status === 'Completed' || a.status === 'Healthy'
        }));
        if (mapped.length) this.agents.set(mapped);
      },
      error: () => {
        console.log('[Dashboard] Backend unavailable — using mock agent data');
      }
    });
  }

  private fetchKnowledgeArticles(): void {
    this.api.getKnowledgeArticles().subscribe({
      next: (data: ArticleResponse[]) => {
        const mapped = data.map(a => ({
          id: a.article_number,
          title: a.title,
          helpful: a.helpful_percentage ?? 0
        }));
        if (mapped.length) this.knowledgeArticles.set(mapped);
      },
      error: () => {
        console.log('[Dashboard] Backend unavailable — using mock KB data');
      }
    });
  }

  private fetchExecutiveMetrics(): void {
    this.api.getExecutiveMetrics().subscribe({
      next: (data: ExecutiveMetricsResponse) => {
        this.execMetrics.set({
          automatedResolution: `${data.automated_resolution ?? 87}%`,
          manualEscalation: `${data.manual_escalation ?? 13}%`,
          avgResolutionTime: data.avg_resolution_minutes != null ? `${data.avg_resolution_minutes}m` : '4m 22s',
          criticalIncidents: String(data.critical_incidents ?? 5)
        });

        // Update KPIs from executive data
        if (data.cyber_hygiene_score != null) {
          this.updateKpi('health', `${data.cyber_hygiene_score}%`, 'Cyber hygiene');
        }
        if (data.automated_resolution != null) {
          this.updateKpi('resolved', String(Math.round(data.automated_resolution)), 'auto-resolved');
        }
      },
      error: () => {
        console.log('[Dashboard] Backend unavailable — using mock executive data');
      }
    });
  }

  private fetchDoraScores(): void {
    this.api.getDoraScores().subscribe({
      next: (data) => {
        if (data.overall_score != null) {
          this.updateKpi('dora', `${data.overall_score}%`, data.audit_ready ? 'Audit Ready' : 'Not Ready');
        }
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        console.log('[Dashboard] Backend unavailable — using mock DORA data');
      }
    });
  }

  /** Trigger the full agent pipeline for a specific incident */
  triggerTriage(incidentNumber: string): void {
    // Extract numeric ID from incident number (e.g. INC548239 → 1 based on position)
    const idx = this.incidents().findIndex(i => i.id === incidentNumber);
    if (idx === -1) return;

    this.api.triageIncident(idx + 1).subscribe({
      next: (result) => {
        console.log('[Dashboard] Triage result:', result);
        // Refresh data after triage
        this.fetchIncidents();
        this.fetchAgents();
      },
      error: (err) => {
        console.error('[Dashboard] Triage failed:', err);
      }
    });
  }

  // ─── Helpers ─────────────────────────────────────────────

  private updateKpi(type: string, value: string, change: string): void {
    const current = this.kpis();
    const updated = current.map(k => k.type === type ? { ...k, value, change } : k);
    this.kpis.set(updated);
  }

  private agentTaskLabel(agent: AgentResponse): string {
    const taskMap: Record<string, string> = {
      'Incident': 'Analyzing incident',
      'Knowledge': 'Searching knowledge base',
      'Infrastructure': 'Checking system services',
      'Network': 'Analyzing network logs',
      'Security': 'Checking known vulnerabilities',
      'Database': 'Scanning database health'
    };
    return taskMap[agent.agent_type] ?? `Running ${agent.agent_type} checks`;
  }

  private formatTime(isoDate: string): string {
    const d = new Date(isoDate);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    if (diffMins < 2880) return 'Yesterday';
    return `${Math.floor(diffMins / 1440)} days ago`;
  }
}