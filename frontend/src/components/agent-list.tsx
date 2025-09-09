import { useState } from 'react';
import { useAgents, useDeleteAgent } from '@/hooks/use-api';
import { Agent } from '@/types/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Trash2, Edit, PlayCircle, CheckCircle } from 'lucide-react';

interface AgentListProps {
  onSelectAgent: (agent: Agent) => void;
  onEditAgent: (agent: Agent) => void;
  onRunAgent: (agent: Agent) => void;
}

export function AgentList({ onSelectAgent, onEditAgent, onRunAgent }: AgentListProps) {
  const [filter, setFilter] = useState<'all' | 'development' | 'completed'>('all');
  const { data, isLoading, error } = useAgents({
    completed: filter === 'all' ? undefined : filter === 'completed',
  });
  const deleteAgent = useDeleteAgent();

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this agent?')) {
      await deleteAgent.mutateAsync(id);
    }
  };

  if (isLoading) return <div className="text-center p-4">Loading agents...</div>;
  if (error) return <div className="text-center p-4 text-red-500">Error loading agents</div>;

  const agents = data?.agents || [];

  return (
    <div className="space-y-4">
      <div className="flex gap-2 mb-4">
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          onClick={() => setFilter('all')}
        >
          All
        </Button>
        <Button
          variant={filter === 'development' ? 'default' : 'outline'}
          onClick={() => setFilter('development')}
        >
          Development
        </Button>
        <Button
          variant={filter === 'completed' ? 'default' : 'outline'}
          onClick={() => setFilter('completed')}
        >
          Completed
        </Button>
      </div>

      {agents.length === 0 ? (
        <Card>
          <CardContent className="text-center p-8">
            <p className="text-muted-foreground">No agents found</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <Card 
              key={agent.id} 
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => onSelectAgent(agent)}
            >
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {agent.name || 'Unnamed Agent'}
                      {agent.complete && (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      )}
                    </CardTitle>
                    <CardDescription>
                      {agent.task_description || 'No description'}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground mb-3">
                  <p>Model: {agent.model_id || 'Not set'}</p>
                  <p>Tools: {agent.tools.length}</p>
                  <p>Integrations: {agent.integrations.join(', ') || 'None'}</p>
                </div>
                <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onEditAgent(agent)}
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onRunAgent(agent)}
                    disabled={!agent.model_id || !agent.instructions}
                  >
                    <PlayCircle className="h-4 w-4 mr-1" />
                    Run
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDelete(agent.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}