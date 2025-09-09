import { useState, useEffect } from 'react';
import { useCreateAgent, useUpdateAgent, useIntegrations, useTools, useModels } from '@/hooks/use-api';
import { Agent } from '@/types/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Loader2, 
  Save, 
  Wand2, 
  CheckCircle, 
  AlertCircle, 
  Play, 
  Download,
  RefreshCw,
  Shield,
  ChevronRight 
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { AgentChat } from './agent-chat';
import { AgentChatStreaming } from './agent-chat-streaming';

interface AgentBuilderEnhancedProps {
  agent?: Agent;
  onSave?: (agent: Agent) => void;
  onCancel?: () => void;
}

// Type definition for build steps

type BuildStep = 'integrations' | 'task' | 'tools' | 'instructions' | 'run';

export function AgentBuilderEnhanced({ agent, onSave, onCancel }: AgentBuilderEnhancedProps) {
  const [currentStep, setCurrentStep] = useState<BuildStep>('integrations');
  const [formData, setFormData] = useState({
    name: agent?.name || '',
    task_description: agent?.task_description || '',
    model_id: agent?.model_id || 'openai:gpt-4.1-mini',
    instructions: agent?.instructions || '',
    integrations: agent?.integrations || [],
    tools: agent?.tools || [],
    evaluations: agent?.evaluations || [],
  });

  const [authStatus, setAuthStatus] = useState<Record<string, { authenticated: boolean; auth_url?: string }>>({});
  const [isCheckingAuth, setIsCheckingAuth] = useState(false);
  const [isGeneratingInstructions, setIsGeneratingInstructions] = useState(false);
  const [isGeneratingTools, setIsGeneratingTools] = useState(false);
  const [toolsWithDescriptions, setToolsWithDescriptions] = useState<Array<{slug: string, description: string}>>([]);
  const [editableInstructions, setEditableInstructions] = useState('');
  const [fullInstructions, setFullInstructions] = useState('');

  const { data: integrationsData } = useIntegrations();
  const { data: modelsData } = useModels();
  const createAgent = useCreateAgent();
  const updateAgent = useUpdateAgent();

  // Check authentication status function
  const checkAuthStatus = async () => {
    setIsCheckingAuth(true);
    const status: Record<string, { authenticated: boolean; auth_url?: string }> = {};
    for (const integration of formData.integrations) {
      try {
        const response = await apiClient.checkAuthStatus(integration, 'default');
        status[integration] = {
          authenticated: response.authenticated,
          auth_url: response.auth_url
        };
      } catch (error) {
        status[integration] = { authenticated: false };
      }
    }
    setAuthStatus(status);
    setIsCheckingAuth(false);
  };

  // Check authentication status for selected integrations
  useEffect(() => {
    if (formData.integrations.length > 0) {
      checkAuthStatus();
    }
  }, [formData.integrations]);

  // Fetch tools when integrations change
  useEffect(() => {
    const fetchTools = async () => {
      if (formData.integrations.length === 0) {
        setToolsWithDescriptions([]);
        return;
      }

      try {
        const response = await apiClient.getComposioTools(formData.integrations);
        const tools = response.tools || [];
        setToolsWithDescriptions(tools);
        
        // Auto-recommend tools if:
        // 1. No tools are selected yet (first time)
        // 2. Task description exists
        // 3. Tools are available
        if (formData.tools.length === 0 && formData.task_description && tools.length > 0) {
          setIsGeneratingTools(true);
          try {
            const recommendResponse = await apiClient.recommendToolsEnhanced(
              formData.task_description,
              tools.map((t: any) => t.slug)
            );
            
            setFormData(prev => ({
              ...prev,
              tools: recommendResponse.tools || [],
            }));
          } catch (error) {
            console.error('Error auto-recommending tools:', error);
          } finally {
            setIsGeneratingTools(false);
          }
        }
      } catch (error) {
        console.error('Error fetching tools:', error);
        setToolsWithDescriptions([]);
      }
    };

    fetchTools();
  }, [formData.integrations, formData.task_description]);

  // Track if we've already auto-recommended tools for this session
  const [hasAutoRecommended, setHasAutoRecommended] = useState(false);

  // Auto-recommend tools when reaching the tools step for the first time
  useEffect(() => {
    const recommendToolsIfNeeded = async () => {
      if (currentStep === 'tools' && 
          formData.tools.length === 0 && 
          formData.task_description && 
          toolsWithDescriptions.length > 0 &&
          !isGeneratingTools &&
          !hasAutoRecommended) {
        console.log('[Tools] Auto-recommending tools for task:', formData.task_description);
        console.log('[Tools] Available tools count:', toolsWithDescriptions.length);
        setHasAutoRecommended(true);
        await handleRecommendTools();
      }
    };

    recommendToolsIfNeeded();
  }, [currentStep, formData.tools.length, formData.task_description, toolsWithDescriptions.length, hasAutoRecommended]);

  // Auto-generate instructions when reaching instructions tab
  useEffect(() => {
    const generateInstructionsIfNeeded = async () => {
      // Only auto-generate if:
      // 1. We're on the instructions tab
      // 2. Instructions are empty
      // 3. We have task description and tools
      // 4. Not already generating
      if (
        currentStep === 'instructions' && 
        !formData.instructions && 
        formData.task_description && 
        formData.tools.length > 0 &&
        !isGeneratingInstructions
      ) {
        console.log('[Instructions] Auto-generating on tab switch...');
        console.log('[Instructions] Task:', formData.task_description);
        console.log('[Instructions] Tools:', formData.tools);
        
        setIsGeneratingInstructions(true);
        try {
          const response = await apiClient.generateInstructionsEnhanced(
            formData.task_description,
            formData.tools
          );
          
          console.log('[Instructions] Auto-gen response:', {
            hasFullInstructions: !!response.instructions,
            hasGeneratedPart: !!response.generated_part,
            fullLength: response.instructions?.length,
            generatedLength: response.generated_part?.length
          });
          
          // Store both full and editable instructions
          setFullInstructions(response.instructions);
          setEditableInstructions(response.generated_part);
          setFormData(prev => ({
            ...prev,
            instructions: response.instructions || '',
          }));
          
          console.log('[Instructions] Auto-generated preview:', response.generated_part?.substring(0, 200));
        } catch (error) {
          console.error('[Instructions] Error auto-generating:', error);
        } finally {
          setIsGeneratingInstructions(false);
          console.log('[Instructions] Auto-generation complete');
        }
      }
    };

    generateInstructionsIfNeeded();
  }, [currentStep, formData.task_description, formData.tools.length]);

  // Determine which steps are available based on completion
  const isStepAvailable = (step: BuildStep): boolean => {
    switch (step) {
      case 'integrations':
        return true;
      case 'task':
        return formData.integrations.length > 0;
      case 'tools':
        return formData.task_description.length > 20; // At least 20 chars
      case 'instructions':
        return formData.tools.length > 0 && formData.model_id !== '';
      case 'run':
        return formData.instructions.length > 50; // At least 50 chars
      default:
        return false;
    }
  };

  const handleGenerateInstructions = async () => {
    if (!formData.task_description || formData.tools.length === 0) {
      alert('Please provide a task description and select tools first');
      return;
    }

    console.log('[Instructions] Starting manual generation...');
    console.log('[Instructions] Task:', formData.task_description);
    console.log('[Instructions] Tools:', formData.tools);
    
    setIsGeneratingInstructions(true);
    try {
      const response = await apiClient.generateInstructionsEnhanced(
        formData.task_description,
        formData.tools
      );
      
      console.log('[Instructions] Response received:', {
        hasFullInstructions: !!response.instructions,
        hasGeneratedPart: !!response.generated_part,
        fullLength: response.instructions?.length,
        generatedLength: response.generated_part?.length
      });
      
      // Store the full instructions and the editable part separately
      setFullInstructions(response.instructions);
      setEditableInstructions(response.generated_part);
      setFormData({
        ...formData,
        instructions: response.instructions,
      });
      
      console.log('[Instructions] Generated part preview:', response.generated_part?.substring(0, 200));
    } catch (error) {
      console.error('[Instructions] Error generating instructions:', error);
    } finally {
      setIsGeneratingInstructions(false);
      console.log('[Instructions] Generation complete');
    }
  };

  const handleRecommendTools = async () => {
    if (!formData.task_description) {
      alert('Please provide a task description first');
      return;
    }

    console.log('[Tools] Starting tool recommendation...');
    console.time('[Tools] Recommendation time');
    setIsGeneratingTools(true);
    try {
      const availableTools = toolsWithDescriptions.map(t => t.slug);
      console.log('[Tools] Sending', availableTools.length, 'tools to recommendation API');
      
      const response = await apiClient.recommendToolsEnhanced(
        formData.task_description,
        availableTools
      );
      
      console.log('[Tools] Recommended tools:', response.tools);
      console.log('[Tools] Recommended tools count:', response.tools?.length || 0);
      setFormData({
        ...formData,
        tools: response.tools || [],
      });
      console.log('[Tools] FormData tools after update:', response.tools || []);
    } catch (error) {
      console.error('[Tools] Error recommending tools:', error);
    } finally {
      setIsGeneratingTools(false);
      console.timeEnd('[Tools] Recommendation time');
    }
  };

  const handleIntegrationToggle = (integration: string) => {
    const newIntegrations = formData.integrations.includes(integration)
      ? formData.integrations.filter(i => i !== integration)
      : [...formData.integrations, integration];
    
    setFormData({
      ...formData,
      integrations: newIntegrations,
      tools: [], // Reset tools when integrations change
    });
  };

  const handleAgentChat = async (message: string, history: any[]) => {
    console.log('[Agent] Sending message:', message);
    console.log('[Agent] History:', history);
    
    try {
      // Use a temporary agent ID for now (could generate UUID)
      const agentId = 'temp-agent-' + Date.now();
      
      const response = await fetch(`/api/agents/${agentId}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: message,
          conversation_history: history,
          agent_config: {
            name: formData.name,
            model_id: formData.model_id,
            task_description: formData.task_description,
            tools: formData.tools,
            instructions: formData.instructions,
          }
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Failed to execute agent: ${error}`);
      }

      const result = await response.json();
      console.log('[Agent] Execution result:', result);
      
      // Return the response so AgentChat can display it
      return result.response;
    } catch (error) {
      console.error('[Agent] Error executing agent:', error);
      throw error;
    }
  };

  const handleToolToggle = (tool: string) => {
    const newTools = formData.tools.includes(tool)
      ? formData.tools.filter(t => t !== tool)
      : [...formData.tools, tool];
    
    setFormData({
      ...formData,
      tools: newTools,
    });
  };

  // Function to reconstruct full instructions when editable part changes
  const updateInstructions = (newEditableText: string) => {
    setEditableInstructions(newEditableText);
    
    // If we have a full instruction template, use it to reconstruct
    if (fullInstructions) {
      // Extract the DEFAULT_SYSTEM_PROMPT (everything before the first double newline after some content)
      const parts = fullInstructions.split('\n\n');
      const DEFAULT_SYSTEM_PROMPT = parts[0]; // The base system prompt
      
      const SPLIT_BEGINNING = "# Reminders";
      const reminderSection = `${SPLIT_BEGINNING}\n- If a tool call fails with an error, don't try the same call again. Instead, try to understand the error and fix the root cause.`;
      
      const newFullInstructions = `${DEFAULT_SYSTEM_PROMPT}\n\n${newEditableText}\n\n${reminderSection}`;
      setFullInstructions(newFullInstructions);
      setFormData({
        ...formData,
        instructions: newFullInstructions
      });
    } else {
      // If no full instructions yet, just set the editable text as instructions
      setFormData({
        ...formData,
        instructions: newEditableText
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      let savedAgent: Agent;
      if (agent) {
        savedAgent = await updateAgent.mutateAsync({
          id: agent.id,
          data: formData,
        });
      } else {
        savedAgent = await createAgent.mutateAsync(formData);
      }
      
      if (onSave) {
        onSave(savedAgent);
      }
    } catch (error) {
      console.error('Error saving agent:', error);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-between mb-6">
      {(['integrations', 'task', 'tools', 'instructions', 'run'] as BuildStep[]).map((step, index) => (
        <div key={step} className="flex items-center">
          <button
            onClick={() => isStepAvailable(step) && setCurrentStep(step)}
            disabled={!isStepAvailable(step)}
            className={`
              flex items-center justify-center w-10 h-10 rounded-full font-medium text-sm
              ${currentStep === step 
                ? 'bg-primary text-primary-foreground' 
                : isStepAvailable(step)
                  ? 'bg-secondary text-secondary-foreground hover:bg-secondary/80 cursor-pointer'
                  : 'bg-muted text-muted-foreground cursor-not-allowed'
              }
            `}
          >
            {index + 1}
          </button>
          {index < 4 && (
            <ChevronRight className={`mx-2 h-4 w-4 ${
              isStepAvailable((['integrations', 'task', 'tools', 'instructions', 'run'] as BuildStep[])[index + 1])
                ? 'text-foreground'
                : 'text-muted-foreground'
            }`} />
          )}
        </div>
      ))}
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{agent ? 'Edit Agent' : 'Create New Agent'}</CardTitle>
          <CardDescription>
            Build your AI agent step by step
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Agent Name - Always Visible */}
          <div>
            <Label htmlFor="name">Agent Name (Optional)</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Leave blank for auto-generated name"
            />
          </div>

          {/* Progressive Disclosure Steps */}
          {renderStepIndicator()}

          <Tabs value={currentStep} onValueChange={(v) => setCurrentStep(v as BuildStep)}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="integrations" disabled={!isStepAvailable('integrations')}>
                Integrations
              </TabsTrigger>
              <TabsTrigger value="task" disabled={!isStepAvailable('task')}>
                Task
              </TabsTrigger>
              <TabsTrigger value="tools" disabled={!isStepAvailable('tools')}>
                Tools
              </TabsTrigger>
              <TabsTrigger value="instructions" disabled={!isStepAvailable('instructions')}>
                Instructions
              </TabsTrigger>
              <TabsTrigger value="run" disabled={!isStepAvailable('run')}>
                Run
              </TabsTrigger>
            </TabsList>

            {/* Step 1: Integrations */}
            <TabsContent value="integrations" className="space-y-4">
              <div>
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <Label>Select Integrations</Label>
                    <p className="text-sm text-muted-foreground">
                      Choose which services your agent can access
                    </p>
                  </div>
                  {formData.integrations.length > 0 && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => checkAuthStatus()}
                      disabled={isCheckingAuth}
                      className="h-8"
                    >
                      {isCheckingAuth ? (
                        <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                      ) : (
                        <RefreshCw className="h-3 w-3 mr-1" />
                      )}
                      {isCheckingAuth ? 'Checking...' : 'Refresh Status'}
                    </Button>
                  )}
                </div>
                <ScrollArea className="h-64 border rounded-lg p-4">
                  <div className="grid grid-cols-2 gap-3">
                    {integrationsData?.integrations.map((integration: string) => (
                      <div key={integration} className="flex items-center justify-between p-2 border rounded">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id={integration}
                            checked={formData.integrations.includes(integration)}
                            onCheckedChange={() => handleIntegrationToggle(integration)}
                          />
                          <label htmlFor={integration} className="text-sm font-medium">
                            {integration}
                          </label>
                        </div>
                        {formData.integrations.includes(integration) && (
                          authStatus[integration]?.authenticated ? (
                            <Badge variant="default" className="ml-2">
                              <CheckCircle className="h-3 w-3 mr-1" /> Connected
                            </Badge>
                          ) : authStatus[integration]?.auth_url ? (
                            <Button
                              size="sm"
                              variant="destructive"
                              className="ml-2 h-6 px-2 text-xs"
                              onClick={(e) => {
                                e.preventDefault();
                                window.open(authStatus[integration].auth_url, '_blank');
                                // Set up a timer to check auth status after opening the auth window
                                setTimeout(() => {
                                  checkAuthStatus();
                                }, 5000); // Check after 5 seconds
                              }}
                            >
                              <AlertCircle className="h-3 w-3 mr-1" /> Connect
                            </Button>
                          ) : (
                            <Badge variant="destructive" className="ml-2">
                              <AlertCircle className="h-3 w-3 mr-1" /> No Auth
                            </Badge>
                          )
                        )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>

                {/* Auth Status Summary */}
                {formData.integrations.length > 0 && (
                  <Alert className="mt-4">
                    <Shield className="h-4 w-4" />
                    <AlertDescription>
                      {Object.values(authStatus).filter(Boolean).length} of {formData.integrations.length} integrations authenticated.
                      {Object.values(authStatus).some(v => !v) && ' Click on unauthenticated integrations to connect.'}
                    </AlertDescription>
                  </Alert>
                )}
              </div>
              
              {/* Navigation buttons */}
              <div className="flex justify-end mt-4">
                <Button
                  onClick={() => setCurrentStep('task')}
                  disabled={!isStepAvailable('task')}
                >
                  Next: Define Task
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </TabsContent>

            {/* Step 2: Task Description */}
            <TabsContent value="task" className="space-y-4">
              <div>
                <Label htmlFor="task_description">Task Description</Label>
                <p className="text-sm text-muted-foreground mb-3">
                  Describe in detail what you want your agent to accomplish
                </p>
                <Textarea
                  id="task_description"
                  value={formData.task_description}
                  onChange={(e) => setFormData({ ...formData, task_description: e.target.value })}
                  placeholder="E.g., Monitor my GitHub repositories for new issues and automatically create Jira tickets for bugs..."
                  rows={6}
                  className="min-h-[150px]"
                />
                {formData.task_description.length < 20 && formData.task_description.length > 0 && (
                  <p className="text-sm text-yellow-600 mt-2">
                    Please provide a more detailed description (at least 20 characters) to proceed
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="model_id">Select Model</Label>
                <Select
                  value={formData.model_id}
                  onValueChange={(value) => setFormData({ ...formData, model_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a model" />
                  </SelectTrigger>
                  <SelectContent>
                    {(modelsData?.models || []).map((model: any) => (
                      <SelectItem key={model.id} value={model.id}>
                        <div className="flex items-center justify-between w-full">
                          <span>{model.name}</span>
                          <Badge variant="outline" className="ml-2">{model.provider}</Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {/* Navigation buttons */}
              <div className="flex justify-between mt-4">
                <Button
                  variant="outline"
                  onClick={() => setCurrentStep('integrations')}
                >
                  <ChevronRight className="mr-2 h-4 w-4 rotate-180" />
                  Back: Integrations
                </Button>
                <Button
                  onClick={() => setCurrentStep('tools')}
                  disabled={!isStepAvailable('tools')}
                >
                  Next: Select Tools
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </TabsContent>

            {/* Step 3: Tools Selection */}
            <TabsContent value="tools" className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <Label>Select Tools</Label>
                    <p className="text-sm text-muted-foreground">
                      Choose tools based on your task requirements
                      {formData.tools.length > 0 && (
                        <span className="ml-2 font-medium">
                          ({formData.tools.length} selected)
                        </span>
                      )}
                    </p>
                  </div>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={handleRecommendTools}
                    disabled={isGeneratingTools || !formData.task_description}
                  >
                    {isGeneratingTools ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <Wand2 className="h-4 w-4 mr-2" />
                    )}
                    {formData.tools.length > 0 ? 'Regenerate Tool Recommendation' : 'AI Recommend'}
                  </Button>
                </div>
                
                <ScrollArea className="h-96 border rounded-lg p-4">
                  {toolsWithDescriptions.length > 0 ? (
                    <div className="space-y-2">
                      {/* Sort tools: selected ones first, then alphabetically */}
                      {[...toolsWithDescriptions]
                        .sort((a, b) => {
                          const aSelected = formData.tools.includes(a.slug);
                          const bSelected = formData.tools.includes(b.slug);
                          if (aSelected && !bSelected) return -1;
                          if (!aSelected && bSelected) return 1;
                          return a.slug.localeCompare(b.slug);
                        })
                        .map((tool) => {
                          const isSelected = formData.tools.includes(tool.slug);
                          return (
                            <div 
                              key={tool.slug} 
                              className={`flex items-start space-x-2 p-2 rounded transition-colors ${
                                isSelected ? 'bg-primary/10 border border-primary/20' : 'hover:bg-secondary/50'
                              }`}
                            >
                              <Checkbox
                                id={tool.slug}
                                checked={isSelected}
                                onCheckedChange={() => handleToolToggle(tool.slug)}
                                className="mt-1"
                              />
                              <div className="flex-1">
                                <label
                                  htmlFor={tool.slug}
                                  className={`text-sm font-medium cursor-pointer ${
                                    isSelected ? 'text-primary' : ''
                                  }`}
                                >
                                  {tool.slug}
                                </label>
                                <p className="text-xs text-muted-foreground mt-1">
                                  {tool.description}
                                </p>
                              </div>
                            </div>
                          );
                        })}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      No tools available. Please select integrations first.
                    </p>
                  )}
                </ScrollArea>
                
                {formData.tools.length > 0 && (
                  <p className="text-sm text-muted-foreground mt-2">
                    {formData.tools.length} tools selected
                  </p>
                )}
              </div>
              
              {/* Navigation buttons */}
              <div className="flex justify-between mt-4">
                <Button
                  variant="outline"
                  onClick={() => setCurrentStep('task')}
                >
                  <ChevronRight className="mr-2 h-4 w-4 rotate-180" />
                  Back: Task
                </Button>
                <Button
                  onClick={() => setCurrentStep('instructions')}
                  disabled={!isStepAvailable('instructions')}
                >
                  Next: Instructions
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </TabsContent>

            {/* Step 4: Instructions */}
            <TabsContent value="instructions" className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <Label htmlFor="instructions">Agent Instructions</Label>
                    <p className="text-sm text-muted-foreground">
                      Detailed instructions for your agent's behavior
                    </p>
                  </div>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={handleGenerateInstructions}
                    disabled={isGeneratingInstructions || !formData.task_description || formData.tools.length === 0}
                  >
                    {isGeneratingInstructions ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <Wand2 className="h-4 w-4 mr-2" />
                    )}
                    {editableInstructions ? 'Regenerate Instructions' : 'AI Generate'}
                  </Button>
                </div>
                
                <div className="relative">
                  {isGeneratingInstructions && !editableInstructions && (
                    <div className="absolute inset-0 bg-background/50 flex items-center justify-center rounded-md z-10">
                      <div className="flex flex-col items-center space-y-2">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                        <span className="text-sm text-muted-foreground">Generating instructions...</span>
                      </div>
                    </div>
                  )}
                  <Textarea
                    id="instructions"
                    value={editableInstructions || ''}
                    onChange={(e) => updateInstructions(e.target.value)}
                    placeholder="Instructions will be auto-generated based on your task and selected tools..."
                    rows={12}
                    className="font-mono text-sm"
                  />
                </div>
                
                {formData.instructions.length > 0 && formData.instructions.length < 50 && (
                  <p className="text-sm text-yellow-600 mt-2">
                    Instructions should be more detailed (at least 50 characters)
                  </p>
                )}
              </div>
              
              {/* Navigation buttons */}
              <div className="flex justify-between mt-4">
                <Button
                  variant="outline"
                  onClick={() => setCurrentStep('tools')}
                >
                  <ChevronRight className="mr-2 h-4 w-4 rotate-180" />
                  Back: Tools
                </Button>
                <Button
                  onClick={() => setCurrentStep('run')}
                  disabled={!isStepAvailable('run')}
                >
                  Next: Run Agent
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </TabsContent>

            {/* Step 5: Run & Test */}
            <TabsContent value="run" className="space-y-4">
              {/* Real-time Streaming Chat */}
              <AgentChatStreaming 
                agentConfig={{
                  name: formData.name || 'Unnamed Agent',
                  model_id: formData.model_id,
                  task_description: formData.task_description,
                  tools: formData.tools,
                  instructions: formData.instructions,
                }}
                useWebSocket={true}
              />

              {/* Agent Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>Configuration Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Name:</span> {formData.name || 'Auto-generated'}
                    </div>
                    <div>
                      <span className="font-medium">Model:</span> {modelsData?.models?.find((m: any) => m.id === formData.model_id)?.name || formData.model_id}
                    </div>
                    <div>
                      <span className="font-medium">Integrations:</span> {formData.integrations.length}
                    </div>
                    <div>
                      <span className="font-medium">Tools:</span> {formData.tools.length}
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <span className="font-medium text-sm">Task:</span>
                    <p className="text-sm text-muted-foreground mt-1">{formData.task_description}</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Cancel Button - Always Visible */}
          {onCancel && (
            <div className="pt-4 border-t">
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </form>
  );
}