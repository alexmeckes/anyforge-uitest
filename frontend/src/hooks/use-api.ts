import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Agent, AgentCreateRequest, AgentUpdateRequest, AgentRunRequest } from '@/types/api';

// Agent hooks
export const useAgents = (params?: { completed?: boolean; page?: number; per_page?: number }) => {
  return useQuery({
    queryKey: ['agents', params],
    queryFn: () => apiClient.listAgents(params),
  });
};

export const useAgent = (id: string) => {
  return useQuery({
    queryKey: ['agent', id],
    queryFn: () => apiClient.getAgent(id),
    enabled: !!id,
  });
};

export const useCreateAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: AgentCreateRequest) => apiClient.createAgent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
};

export const useUpdateAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AgentUpdateRequest }) => 
      apiClient.updateAgent(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['agent', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
};

export const useDeleteAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => apiClient.deleteAgent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
};

export const useRunAgent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AgentRunRequest }) => 
      apiClient.runAgent(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['agent', variables.id, 'traces'] });
    },
  });
};

export const useAgentTraces = (id: string) => {
  return useQuery({
    queryKey: ['agent', id, 'traces'],
    queryFn: () => apiClient.getAgentTraces(id),
    enabled: !!id,
  });
};

// Integration hooks
export const useIntegrations = () => {
  return useQuery({
    queryKey: ['integrations'],
    queryFn: () => apiClient.listIntegrations(),
  });
};

export const useIntegrationStatus = (integrations?: string[]) => {
  return useQuery({
    queryKey: ['integrations', 'status', integrations],
    queryFn: () => apiClient.getIntegrationStatus(integrations),
  });
};

export const useAuthenticateIntegration = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ name, redirectUrl }: { name: string; redirectUrl?: string }) => 
      apiClient.authenticateIntegration(name, redirectUrl),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
    },
  });
};

// Tools hooks
export const useRecommendTools = () => {
  return useMutation({
    mutationFn: ({ taskDescription, integrations }: { 
      taskDescription: string; 
      integrations: string[] 
    }) => apiClient.recommendTools(taskDescription, integrations),
  });
};

export const useGenerateInstructions = () => {
  return useMutation({
    mutationFn: ({ taskDescription, tools }: { 
      taskDescription: string; 
      tools: string[] 
    }) => apiClient.generateInstructions(taskDescription, tools),
  });
};

export const useTools = (integrations?: string[]) => {
  return useQuery({
    queryKey: ['tools', integrations],
    queryFn: () => apiClient.listTools(integrations),
    enabled: integrations === undefined || integrations.length > 0,
  });
};

// Models hooks
export const useModels = () => {
  return useQuery({
    queryKey: ['models'],
    queryFn: () => apiClient.listModels(),
  });
};