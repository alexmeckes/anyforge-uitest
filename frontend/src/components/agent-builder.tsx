import { useState, useEffect } from 'react';
import { useCreateAgent, useUpdateAgent, useIntegrations, useRecommendTools, useGenerateInstructions, useTools } from '@/hooks/use-api';
import { Agent } from '@/types/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Loader2, Save, Wand2 } from 'lucide-react';

interface AgentBuilderProps {
  agent?: Agent;
  onSave?: (agent: Agent) => void;
  onCancel?: () => void;
}

const AVAILABLE_MODELS = [
  { id: 'gpt-4-turbo', name: 'GPT-4 Turbo' },
  { id: 'gpt-4', name: 'GPT-4' },
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
  { id: 'claude-3-opus', name: 'Claude 3 Opus' },
  { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet' },
];

export function AgentBuilder({ agent, onSave, onCancel }: AgentBuilderProps) {
  const [formData, setFormData] = useState({
    name: agent?.name || '',
    task_description: agent?.task_description || '',
    model_id: agent?.model_id || '',
    instructions: agent?.instructions || '',
    integrations: agent?.integrations || [],
    tools: agent?.tools || [],
  });

  const { data: integrationsData } = useIntegrations();
  const { data: toolsData } = useTools(formData.integrations);
  const createAgent = useCreateAgent();
  const updateAgent = useUpdateAgent();
  const recommendTools = useRecommendTools();
  const generateInstructions = useGenerateInstructions();

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

  const handleRecommendTools = async () => {
    if (!formData.task_description) {
      alert('Please provide a task description first');
      return;
    }

    try {
      const result = await recommendTools.mutateAsync({
        taskDescription: formData.task_description,
        integrations: formData.integrations,
      });
      
      setFormData({
        ...formData,
        tools: result.recommended_tools,
      });
    } catch (error) {
      console.error('Error recommending tools:', error);
    }
  };

  const handleGenerateInstructions = async () => {
    if (!formData.task_description || formData.tools.length === 0) {
      alert('Please provide a task description and select tools first');
      return;
    }

    try {
      const result = await generateInstructions.mutateAsync({
        taskDescription: formData.task_description,
        tools: formData.tools,
      });
      
      setFormData({
        ...formData,
        instructions: result.instructions,
      });
    } catch (error) {
      console.error('Error generating instructions:', error);
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

  const handleToolToggle = (tool: string) => {
    const newTools = formData.tools.includes(tool)
      ? formData.tools.filter(t => t !== tool)
      : [...formData.tools, tool];
    
    setFormData({
      ...formData,
      tools: newTools,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{agent ? 'Edit Agent' : 'Create New Agent'}</CardTitle>
          <CardDescription>
            Configure your AI agent with specific capabilities and instructions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="name">Agent Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="My Custom Agent"
            />
          </div>

          <div>
            <Label htmlFor="task_description">Task Description</Label>
            <Textarea
              id="task_description"
              value={formData.task_description}
              onChange={(e) => setFormData({ ...formData, task_description: e.target.value })}
              placeholder="Describe what this agent should do..."
              rows={3}
            />
          </div>

          <div>
            <Label htmlFor="model_id">Model</Label>
            <Select
              value={formData.model_id}
              onValueChange={(value) => setFormData({ ...formData, model_id: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_MODELS.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Integrations</Label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-2">
              {integrationsData?.integrations.map((integration: string) => (
                <div key={integration} className="flex items-center space-x-2">
                  <Checkbox
                    id={integration}
                    checked={formData.integrations.includes(integration)}
                    onCheckedChange={() => handleIntegrationToggle(integration)}
                  />
                  <label
                    htmlFor={integration}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    {integration}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <Label>Tools</Label>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={handleRecommendTools}
                disabled={recommendTools.isPending}
              >
                {recommendTools.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-1" />
                ) : (
                  <Wand2 className="h-4 w-4 mr-1" />
                )}
                Recommend Tools
              </Button>
            </div>
            <div className="border rounded-lg p-3 max-h-48 overflow-y-auto">
              {toolsData?.tools?.length > 0 ? (
                <div className="space-y-2">
                  {toolsData.tools.map((tool: string) => (
                    <div key={tool} className="flex items-center space-x-2">
                      <Checkbox
                        id={tool}
                        checked={formData.tools.includes(tool)}
                        onCheckedChange={() => handleToolToggle(tool)}
                      />
                      <label
                        htmlFor={tool}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        {tool}
                      </label>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Select integrations to see available tools
                </p>
              )}
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <Label htmlFor="instructions">Instructions</Label>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={handleGenerateInstructions}
                disabled={generateInstructions.isPending}
              >
                {generateInstructions.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-1" />
                ) : (
                  <Wand2 className="h-4 w-4 mr-1" />
                )}
                Generate Instructions
              </Button>
            </div>
            <Textarea
              id="instructions"
              value={formData.instructions}
              onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
              placeholder="Provide detailed instructions for the agent..."
              rows={6}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              disabled={createAgent.isPending || updateAgent.isPending}
            >
              {createAgent.isPending || updateAgent.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {agent ? 'Update Agent' : 'Create Agent'}
                </>
              )}
            </Button>
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </form>
  );
}