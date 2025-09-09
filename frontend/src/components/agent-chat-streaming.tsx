import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Send, Trash2, Loader2, User, Bot, Wrench, WifiOff, Wifi } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAgentWebSocket } from '@/hooks/useAgentWebSocket';

interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp?: Date;
  metadata?: any;
}

interface AgentChatStreamingProps {
  agentConfig: {
    name?: string;
    model_id?: string;
    task_description?: string;
    tools?: string[];
    instructions?: string;
  };
  useWebSocket?: boolean;
}

export function AgentChatStreaming({ agentConfig, useWebSocket = true }: AgentChatStreamingProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // WebSocket hook for real-time streaming
  const {
    isConnected,
    isLoading,
    sendMessage: sendWebSocketMessage,
    connect,
    disconnect
  } = useAgentWebSocket({
    onMessage: (message) => {
      setMessages(prev => [...prev, message]);
      setStatusMessage('');
    },
    onStatusUpdate: (status) => {
      setStatusMessage(status);
    },
    onError: (error) => {
      const errorMessage: Message = {
        role: 'system',
        content: `Error: ${error}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setStatusMessage('');
    },
    onComplete: () => {
      setStatusMessage('');
    }
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages, statusMessage]);

  const handleClearChat = () => {
    setMessages([]);
    setInputMessage('');
    setStatusMessage('');
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    if (useWebSocket && isConnected) {
      // Use WebSocket for real-time streaming
      await sendWebSocketMessage(inputMessage, agentConfig, messages);
    } else {
      // Fallback to HTTP (could implement the old approach here)
      const errorMessage: Message = {
        role: 'system',
        content: 'WebSocket not connected. Please check your connection.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageIcon = (role: string) => {
    switch (role) {
      case 'user':
        return <User className="h-6 w-6 text-primary" />;
      case 'assistant':
        return <Bot className="h-6 w-6 text-primary" />;
      case 'tool':
        return <Wrench className="h-6 w-6 text-blue-500" />;
      default:
        return <div className="h-6 w-6 rounded-full bg-yellow-500/20 flex items-center justify-center">
          <span className="text-xs">!</span>
        </div>;
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <CardTitle>Chat with {agentConfig.name || 'Agent'}</CardTitle>
              {useWebSocket && (
                <Badge variant={isConnected ? "default" : "secondary"} className="gap-1">
                  {isConnected ? (
                    <>
                      <Wifi className="h-3 w-3" />
                      Live
                    </>
                  ) : (
                    <>
                      <WifiOff className="h-3 w-3" />
                      Offline
                    </>
                  )}
                </Badge>
              )}
            </div>
            <div className="flex gap-2">
              {!isConnected && useWebSocket && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={connect}
                >
                  Reconnect
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearChat}
                disabled={messages.length === 0}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Clear Chat
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Agent Info */}
            {agentConfig.task_description && (
              <div className="text-sm text-muted-foreground bg-secondary/50 p-3 rounded-lg">
                <strong>Task:</strong> {agentConfig.task_description}
              </div>
            )}

            {/* Messages Area */}
            <ScrollArea className="h-[400px] border rounded-lg p-4" ref={scrollAreaRef}>
              {messages.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  <Bot className="h-12 w-12 mx-auto mb-4 text-muted-foreground/50" />
                  <p>Start a conversation with your agent</p>
                  <p className="text-sm mt-2">
                    {useWebSocket ? 'Responses will stream in real-time' : 'Type a message below to begin'}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={cn(
                        'flex gap-3',
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      {message.role !== 'user' && (
                        <div className="flex-shrink-0">
                          {getMessageIcon(message.role)}
                        </div>
                      )}
                      <div
                        className={cn(
                          'rounded-lg px-4 py-2 max-w-[80%]',
                          message.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : message.role === 'assistant'
                            ? 'bg-secondary'
                            : message.role === 'tool'
                            ? 'bg-blue-500/10 border border-blue-500/20'
                            : 'bg-yellow-500/10 border border-yellow-500/20'
                        )}
                      >
                        {message.role === 'tool' && message.metadata?.tool && (
                          <div className="text-xs font-semibold mb-1 text-blue-600">
                            Tool: {message.metadata.tool}
                          </div>
                        )}
                        <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                        {message.timestamp && (
                          <div className="text-xs opacity-70 mt-1">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        )}
                      </div>
                      {message.role === 'user' && (
                        <div className="flex-shrink-0">
                          {getMessageIcon(message.role)}
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {/* Status Message or Loading */}
                  {(isLoading || statusMessage) && (
                    <div className="flex gap-3 justify-start">
                      <Bot className="h-6 w-6 text-primary" />
                      <div className="bg-secondary rounded-lg px-4 py-2">
                        {statusMessage ? (
                          <div className="text-sm text-muted-foreground italic">{statusMessage}</div>
                        ) : (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>

            {/* Input Area */}
            <div className="flex gap-2">
              <Input
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={isConnected ? "Type your message..." : "Connecting to WebSocket..."}
                disabled={isLoading || (!isConnected && useWebSocket)}
                className="flex-1"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading || (!isConnected && useWebSocket)}
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Tools Info */}
            {agentConfig.tools && agentConfig.tools.length > 0 && (
              <div className="text-xs text-muted-foreground">
                <strong>Available tools:</strong> {agentConfig.tools.join(', ')}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}