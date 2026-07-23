// ─── Models matching backend Pydantic schemas exactly ───

// --- Incidents ---
export interface IncidentResponse {
  incident_id: number;
  incident_number: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  affected_users: number | null;
  application: string | null;
  platform: string | null;
  ci_criticality: string | null;
  classification: string | null;
  classification_confidence: number | null;
  hop_count: number | null;
  current_owner: string | null;
  created_at: string | null;
  resolved_at: string | null;
}

export interface TriageResponse {
  incident_id: number;
  classification: string;
  confidence: number;
  resolution: string | null;
  current_owner: string;
  hop_count: number;
  message: string;
}

// --- Agents ---
export interface AgentResponse {
  agent_id: number;
  agent_name: string;
  agent_type: string;
  status: string;
  confidence_score: number | null;
}

// --- Chat Room ---
export interface MessageResponse {
  message_id: number;
  sender_type: string;
  sender_name: string;
  content: string;
  message_type: string;
  metadata_json: string | null;
  created_at: string | null;
}

export interface ChatRoomResponse {
  room_id: number;
  incident_id: number;
  status: string;
  messages: MessageResponse[];
  agent_names: string[];
  member_names: string[];
}

export interface SendMessageRequest {
  user_id: number;
  content: string;
}

export interface AddAgentRequest {
  agent_id: number;
}

export interface AddMemberRequest {
  user_id: number;
}

export interface ApprovalRequest {
  message_id: number;
  approved: boolean;
  user_id: number;
}

// --- Knowledge ---
export interface ArticleResponse {
  article_id: number;
  article_number: string;
  title: string;
  category: string | null;
  keywords: string | null;
  content: string | null;
  helpful_percentage: number | null;
  status: string | null;
  updated_date: string | null;
}

export interface ArticleSearchResult {
  article_number: string;
  title: string;
  category: string;
  score: number;
}

// --- Dashboard ---
export interface ExecutiveMetricsResponse {
  metric_date: string | null;
  automated_resolution: number | null;
  manual_escalation: number | null;
  avg_resolution_minutes: number | null;
  critical_incidents: number | null;
  dora_score: number | null;
  cyber_hygiene_score: number | null;
}

export interface DoraResponse {
  operational_resilience: number | null;
  ict_risk: number | null;
  incident_management: number | null;
  business_continuity: number | null;
  third_party_risk: number | null;
  overall_score: number | null;
  audit_ready: boolean | null;
}

// --- Escalation ---
export interface EscalationResponse {
  escalation_id: number;
  incident_id: number;
  assigned_team: string;
  engineer_name: string;
  reason: string;
  estimated_wait: number;
  status: string;
}

// --- WebSocket event shape ---
export interface WsEvent {
  type: 'article_list' | 'text' | 'system' | 'approval_request' | 'approval_response' | 'member_joined';
  data: any;
}
