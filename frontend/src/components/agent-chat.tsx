import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Send, Trash2, Loader2, User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: Date;
}

interface AgentChatProps {
  agentConfig: {
    name?: string;
    model_id?: string;
    task_description?: string;
    tools?: string[];
    instructions?: string;
  };
  onSendMessage?: (message: string, history: Message[]) => Promise<string | void>;
}

export function AgentChat({ agentConfig, onSendMessage }: AgentChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const handleClearChat = () => {
    setMessages([]);
    setInputMessage('');
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
    setIsLoading(true);

    try {
      if (onSendMessage) {
        const response = await onSendMessage(inputMessage, [...messages, userMessage]);
        
        // Add the assistant's response to the messages
        if (response) {
          const assistantMessage: Message = {
            role: 'assistant',
            content: response,
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, assistantMessage]);
        }
      } else {
        // Mock response for testing
        setTimeout(() => {
          const assistantMessage: Message = {
            role: 'assistant',
            content: `I received your message: "${inputMessage}". The agent functionality is being implemented.`,
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, assistantMessage]);
          setIsLoading(false);
        }, 1000);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Chat with {agentConfig.name || 'Agent'}</CardTitle>
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
                  <p className="text-sm mt-2">Type a message below to begin</p>
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
                          {message.role === 'assistant' ? (
                            <Bot className="h-6 w-6 text-primary" />
                          ) : (
                            <div className="h-6 w-6 rounded-full bg-yellow-500/20 flex items-center justify-center">
                              <span className="text-xs">!</span>
                            </div>
                          )}
                        </div>
                      )}
                      <div
                        className={cn(
                          'rounded-lg px-4 py-2 max-w-[80%]',
                          message.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : message.role === 'assistant'
                            ? 'bg-secondary'
                            : 'bg-yellow-500/10 border border-yellow-500/20'
                        )}
                      >
                        <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                        {message.timestamp && (
                          <div className="text-xs opacity-70 mt-1">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        )}
                      </div>
                      {message.role === 'user' && (
                        <div className="flex-shrink-0">
                          <User className="h-6 w-6 text-primary" />
                        </div>
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex gap-3 justify-start">
                      <Bot className="h-6 w-6 text-primary" />
                      <div className="bg-secondary rounded-lg px-4 py-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
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
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
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
                <strong>Available tools:</strong> {agentConfig.tools.length} tools configured
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}