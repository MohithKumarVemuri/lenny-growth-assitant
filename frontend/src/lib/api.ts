export interface SourceCitation {
  episode: string;
  guest: string;
  timestamp?: string;
  score: number;
  text: string;
  url?: string;
}

export interface Artifact {
  id?: string;
  session_id?: string;
  title: string;
  type: string; // 'html' | 'markdown'
  content: string;
  language?: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: SourceCitation[];
  model_provider: string;
  mode: string;
  created_at?: string;
  artifacts?: Artifact[];
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail extends Session {
  messages: Message[];
  artifacts: Artifact[];
}

export interface HealthData {
  status: string;
  database_mode: string;
  vector_count: number;
  default_provider: string;
  ollama_status: {
    online: boolean;
    base_url: string;
    target_model: string;
    installed_models: string[];
  };
  cloud_configured: {
    anthropic: boolean;
    openai: boolean;
  };
}

export const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

export async function fetchHealth(): Promise<HealthData> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchSessions(): Promise<Session[]> {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error('Failed to load sessions');
  return res.json();
}

export async function createSession(title: string = 'New Conversation'): Promise<Session> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function fetchSessionDetail(sessionId: string): Promise<SessionDetail> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) throw new Error('Failed to fetch session detail');
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete session');
}
