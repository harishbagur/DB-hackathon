import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  IncidentResponse,
  TriageResponse,
  AgentResponse,
  ChatRoomResponse,
  MessageResponse,
  SendMessageRequest,
  AddAgentRequest,
  AddMemberRequest,
  ApprovalRequest,
  ArticleResponse,
  ArticleSearchResult,
  ExecutiveMetricsResponse,
  DoraResponse,
  EscalationResponse
} from '../models/api.models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(private http: HttpClient) {}

  // ─── Incidents ───────────────────────────────────────────

  getIncidents(): Observable<IncidentResponse[]> {
    return this.http.get<IncidentResponse[]>('/api/incidents');
  }

  getIncident(id: number): Observable<IncidentResponse> {
    return this.http.get<IncidentResponse>(`/api/incidents/${id}`);
  }

  triageIncident(id: number): Observable<TriageResponse> {
    return this.http.post<TriageResponse>(`/api/incidents/${id}/triage`, {});
  }

  // ─── Agents ──────────────────────────────────────────────

  getAgents(): Observable<AgentResponse[]> {
    return this.http.get<AgentResponse[]>('/api/agents');
  }

  // ─── Chat Room ───────────────────────────────────────────

  getRoom(incidentId: number): Observable<ChatRoomResponse> {
    return this.http.get<ChatRoomResponse>(`/api/incidents/${incidentId}/room`);
  }

  addAgentToRoom(incidentId: number, payload: AddAgentRequest): Observable<any> {
    return this.http.post(`/api/incidents/${incidentId}/room/agents`, payload);
  }

  addMemberToRoom(incidentId: number, payload: AddMemberRequest): Observable<any> {
    return this.http.post(`/api/incidents/${incidentId}/room/members`, payload);
  }

  sendMessage(incidentId: number, payload: SendMessageRequest): Observable<MessageResponse> {
    return this.http.post<MessageResponse>(`/api/incidents/${incidentId}/room/messages`, payload);
  }

  handleApproval(incidentId: number, payload: ApprovalRequest): Observable<any> {
    return this.http.post(`/api/incidents/${incidentId}/room/approve`, payload);
  }

  getAssignmentGroup(incidentId: number): Observable<any> {
    return this.http.get(`/api/incidents/${incidentId}/escalation/group`);
  }

  // ─── Knowledge ───────────────────────────────────────────

  getKnowledgeArticles(): Observable<ArticleResponse[]> {
    return this.http.get<ArticleResponse[]>('/api/knowledge');
  }

  searchKnowledge(query: string): Observable<ArticleSearchResult[]> {
    const params = new HttpParams().set('q', query);
    return this.http.get<ArticleSearchResult[]>('/api/knowledge/search', { params });
  }

  approveKnowledgeArticle(id: number): Observable<ArticleResponse> {
    return this.http.patch<ArticleResponse>(`/api/knowledge/${id}/approve`, {});
  }

  // ─── Dashboard ───────────────────────────────────────────

  getExecutiveMetrics(): Observable<ExecutiveMetricsResponse> {
    return this.http.get<ExecutiveMetricsResponse>('/api/dashboard/executive');
  }

  getDoraScores(): Observable<DoraResponse> {
    return this.http.get<DoraResponse>('/api/dashboard/dora');
  }

  // ─── Escalation ──────────────────────────────────────────

  getEscalation(incidentId: number): Observable<EscalationResponse> {
    return this.http.get<EscalationResponse>(`/api/incidents/${incidentId}/escalation`);
  }

  // ─── Gemini Integration ──────────────────────────────────

  chatGemini(message: string, history: any[] = []): Observable<{ response: string }> {
    return this.http.post<{ response: string }>('/api/gemini/chat', { message, history });
  }
}
