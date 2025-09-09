export interface Agent {
  id: string;
  name?: string;
  integrations: string[];
  task_description?: string;
  model_id?: string;
  instructions?: string;
  tools: string[];
  evaluations?: string[];
  complete: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AgentCreateRequest {
  name?: string;
  integrations?: string[];
  task_description?: string;
  model_id?: string;
  instructions?: string;
  tools?: string[];
}

export interface AgentUpdateRequest {
  name?: string;
  integrations?: string[];
  task_description?: string;
  model_id?: string;
  instructions?: string;
  tools?: string[];
  complete?: boolean;
}

export interface AgentRunRequest {
  prompt: string;
  conversation_history?: ConversationMessage[];
  run_kwargs?: Record<string, any>;
}

export interface ConversationMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface TraceResponse {
  id: string;
  agent_id: string;
  prompt: string;
  result?: string;
  error?: string;
  spans: any[];
  created_at: string;
}

export interface IntegrationStatus {
  integration: string;
  is_authenticated: boolean;
  error_message?: string;
  connection_id?: string;
}

export interface IntegrationListResponse {
  integrations: string[];
  authenticated: string[];
}

export interface ToolRecommendationResponse {
  recommended_tools: string[];
  reasoning?: string;
}

export interface InstructionGenerationResponse {
  instructions: string;
  confidence?: number;
}

export interface WSMessage {
  type: string;
  timestamp: string;
}

export interface WSAgentStatus extends WSMessage {
  type: 'status';
  status: 'starting' | 'running' | 'completed' | 'failed';
  message?: string;
}

export interface WSAgentOutput extends WSMessage {
  type: 'output';
  content: string;
  role: 'assistant' | 'tool' | 'system';
}

export interface WSToolCall extends WSMessage {
  type: 'tool_call';
  tool_name: string;
  arguments: Record<string, any>;
}

export interface WSToolResult extends WSMessage {
  type: 'tool_result';
  tool_name: string;
  result?: any;
  error?: string;
}

export interface WSError extends WSMessage {
  type: 'error';
  error: string;
  detail?: string;
}

export interface WSComplete extends WSMessage {
  type: 'complete';
  trace_id: string;
  final_answer?: string;
}