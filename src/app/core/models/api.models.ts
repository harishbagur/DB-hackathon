export interface Incident {
  id?: string;
  incident_id?: number;
  incident_number: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  affected_users?: number;
  application?: string;
  root_cause?: string;
  created_at?: string;
  resolved_at?: string;
  current_owner?: string;
  hop_count?: number;
  actions_attempted?: any[];
  diagnostics_collected?: string[];
  hypothesis?: string;
  escalation_reason?: string | null;
  // added for compatibility with backend responses
  [key: string]: any;
}

export interface Agent {
  agent_id?: number;
  agent_name: string;
  agent_type: string;
  status: string;
  confidence_score?: number;
  [key: string]: any;
}

export interface RoomMessage {
  id?: string;
  incident_id: string;
  sender_name: string;
  sender_role: string;
  content: string;
  timestamp: string;
  [key: string]: any;
}

export interface Room {
  incident_id: string;
  messages: RoomMessage[];
  members: any[];
  agents: Agent[];
}

export interface KnowledgeArticle {
  article_id?: number;
  article_number: string;
  title: string;
  category: string;
  keywords: string;
  helpful_percentage: number;
  updated_date: string;
  [key: string]: any;
}

export interface ExecutiveMetrics {
  metric_id?: number;
  metric_date?: string;
  automated_resolution: number;
  manual_escalation: number;
  avg_resolution_minutes: number;
  critical_incidents: number;
  dora_score: number;
  cyber_hygiene_score: number;
}

export interface DoraCompliance {
  compliance_id?: number;
  operational_resilience: number;
  ict_risk: number;
  incident_management: number;
  business_continuity: number;
  third_party_risk: number;
  overall_score: number;
  audit_ready: boolean;
}

export interface Escalation {
  escalation_id?: number;
  incident_id?: number;
  assigned_team: string;
  engineer_name: string;
  reason: string;
  estimated_wait: number;
  status: string;
}
