export interface Memory {
  id: string;
  content: string;
  timestamp: string;
  tags: string[];
}

export interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: string;
  image?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  llm_provider: string;
  oauth_provider?: string;
  created_at: string;
  user_settings?: UserSettings;
}

export interface UserSettings {
  id: number;
  user_id: number;
  memory_retention_days: number;
  max_memories_per_topic: number;
  default_search_type: string;
  default_scope: string;
  embedding_model: string;
  language_preference: string;
  additional_settings?: Record<string, any>;
}

export type Provider = 'openai' | 'anthropic' | 'cohere' | 'groq';

export interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface Topic {
  id: number;
  name: string;
  description?: string;
  scope: string;
  created_at: string;
}

export type Scope = 'personal' | 'project' | 'team';

export type SearchType = 'keyword' | 'vector' | 'time';
