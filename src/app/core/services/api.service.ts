import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Incident,
  Agent,
  Room,
  RoomMessage,
  KnowledgeArticle,
  ExecutiveMetrics,
  DoraCompliance,
  Escalation
} from '../models/api.models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly basePath = '/api';

  constructor(private http: HttpClient) {}

  // Incidents
  getIncidents(): Observable<Incident[]> {
    return this.http.get<Incident[]>(`${this.basePath}/incidents`);
  }

  getIncident(id: string): Observable<Incident> {
    return this.http.get<Incident>(`${this.basePath}/incidents/${id}`);
  }

  triageIncident(id: string): Observable<any> {
    return this.http.post<any>(`${this.basePath}/incidents/${id}/triage`, {});
  }

  // Agents
  getAgents(): Observable<Agent[]> {
    return this.http.get<Agent[]>(`${this.basePath}/agents`);
  }

  // Chat Room
  getRoom(incidentId: string): Observable<Room> {
    return this.http.get<Room>(`${this.basePath}/incidents/${incidentId}/room`);
  }

  addAgentToRoom(incidentId: string, payload: any): Observable<any> {
    return this.http.post<any>(`${this.basePath}/incidents/${incidentId}/room/agents`, payload);
  }

  addMemberToRoom(incidentId: string, payload: any): Observable<any> {
    return this.http.post<any>(`${this.basePath}/incidents/${incidentId}/room/members`, payload);
  }

  sendMessage(incidentId: string, payload: any): Observable<any> {
    return this.http.post<any>(`${this.basePath}/incidents/${incidentId}/room/messages`, payload);
  }

  // Knowledge
  getKnowledgeArticles(): Observable<KnowledgeArticle[]> {
    return this.http.get<KnowledgeArticle[]>(`${this.basePath}/knowledge`);
  }

  searchKnowledge(query: string): Observable<KnowledgeArticle[]> {
    return this.http.get<KnowledgeArticle[]>(`${this.basePath}/knowledge/search`, {
      params: { q: query }
    });
  }

  approveKnowledgeArticle(id: string): Observable<any> {
    return this.http.patch<any>(`${this.basePath}/knowledge/${id}/approve`, {});
  }

  // Dashboard
  getExecutiveMetrics(): Observable<ExecutiveMetrics> {
    return this.http.get<ExecutiveMetrics>(`${this.basePath}/dashboard/executive`);
  }

  getDoraScores(): Observable<DoraCompliance> {
    return this.http.get<DoraCompliance>(`${this.basePath}/dashboard/dora`);
  }

  // Escalation
  getEscalation(incidentId: string): Observable<Escalation> {
    return this.http.get<Escalation>(`${this.basePath}/incidents/${incidentId}/escalation`);
  }
}
