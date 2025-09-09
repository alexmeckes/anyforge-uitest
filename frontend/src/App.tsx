import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AgentList } from '@/components/agent-list';
import { AgentBuilder } from '@/components/agent-builder';
import { AgentBuilderEnhanced } from '@/components/agent-builder-enhanced';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Agent } from '@/types/api';
import { Plus, List, Settings } from 'lucide-react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

type ViewMode = 'list' | 'create' | 'edit' | 'run';

function AppContent() {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedAgent, setSelectedAgent] = useState<Agent | undefined>();

  const handleSelectAgent = (agent: Agent) => {
    setSelectedAgent(agent);
    setViewMode('edit');
  };

  const handleEditAgent = (agent: Agent) => {
    setSelectedAgent(agent);
    setViewMode('edit');
  };

  const handleRunAgent = (agent: Agent) => {
    setSelectedAgent(agent);
    setViewMode('run');
    // TODO: Implement agent runner component
  };

  const handleSaveAgent = (agent: Agent) => {
    setViewMode('list');
    setSelectedAgent(undefined);
  };

  const handleCancel = () => {
    setViewMode('list');
    setSelectedAgent(undefined);
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">Any-Forge</h1>
              <p className="text-muted-foreground">AI Agent Builder</p>
            </div>
            <div className="flex gap-2">
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                onClick={() => setViewMode('list')}
              >
                <List className="h-4 w-4 mr-2" />
                All Agents
              </Button>
              <Button
                variant={viewMode === 'create' ? 'default' : 'outline'}
                onClick={() => {
                  setSelectedAgent(undefined);
                  setViewMode('create');
                }}
              >
                <Plus className="h-4 w-4 mr-2" />
                New Agent
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {viewMode === 'list' && (
          <AgentList
            onSelectAgent={handleSelectAgent}
            onEditAgent={handleEditAgent}
            onRunAgent={handleRunAgent}
          />
        )}

        {viewMode === 'create' && (
          <AgentBuilderEnhanced
            onSave={handleSaveAgent}
            onCancel={handleCancel}
          />
        )}

        {viewMode === 'edit' && selectedAgent && (
          <AgentBuilderEnhanced
            agent={selectedAgent}
            onSave={handleSaveAgent}
            onCancel={handleCancel}
          />
        )}

        {viewMode === 'run' && selectedAgent && (
          <Card>
            <CardHeader>
              <CardTitle>Run Agent: {selectedAgent.name || 'Unnamed'}</CardTitle>
              <CardDescription>
                Agent runner coming soon. This will include chat interface and real-time streaming.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={handleCancel}>Back to List</Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;