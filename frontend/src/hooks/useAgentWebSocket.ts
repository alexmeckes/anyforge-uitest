import { useEffect, useRef, useState, useCallback } from 'react';

interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp?: Date;
  metadata?: any;
}

interface WebSocketMessage {
  type: 'assistant_message' | 'tool_execution' | 'status' | 'completion' | 'error' | 'pong';
  content: string;
  metadata?: any;
  timestamp?: string;
}

interface UseAgentWebSocketOptions {
  onMessage?: (message: Message) => void;
  onStatusUpdate?: (status: string) => void;
  onError?: (error: string) => void;
  onComplete?: () => void;
}

export function useAgentWebSocket(options: UseAgentWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const pingIntervalRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    // Prevent multiple simultaneous connection attempts
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    const wsUrl = `ws://localhost:8003/ws/agent/${sessionId}`;
    console.log(`[WebSocket] Connecting to ${wsUrl}`);
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[WebSocket] Connected');
      setIsConnected(true);
      
      // Start ping interval to keep connection alive
      pingIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000); // Ping every 30 seconds
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        console.log('[WebSocket] Received:', data);

        switch (data.type) {
          case 'assistant_message':
            options.onMessage?.({
              role: 'assistant',
              content: data.content,
              timestamp: new Date(data.timestamp || Date.now()),
              metadata: data.metadata
            });
            break;

          case 'tool_execution':
            options.onMessage?.({
              role: 'tool',
              content: data.content,
              timestamp: new Date(data.timestamp || Date.now()),
              metadata: data.metadata
            });
            break;

          case 'status':
            options.onStatusUpdate?.(data.content);
            if (data.metadata?.status === 'starting') {
              setIsLoading(true);
            }
            break;

          case 'completion':
            setIsLoading(false);
            options.onComplete?.();
            break;

          case 'error':
            setIsLoading(false);
            options.onError?.(data.content);
            break;

          case 'pong':
            // Connection is alive
            break;
        }
      } catch (error) {
        console.error('[WebSocket] Error parsing message:', error);
      }
    };

    ws.onerror = (error) => {
      console.warn('[WebSocket] Connection error (will retry):', error);
      // Don't call onError for connection errors - these are handled by onclose
    };

    ws.onclose = () => {
      console.log('[WebSocket] Disconnected');
      setIsConnected(false);
      setIsLoading(false);
      
      // Clear ping interval
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
      
      // Clean up the WebSocket reference
      wsRef.current = null;
      
      // Attempt to reconnect after 5 seconds (increased from 3)
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('[WebSocket] Attempting to reconnect...');
        connect();
      }, 5000);
    };
  }, [sessionId, options]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsLoading(false);
  }, []);

  const sendMessage = useCallback(async (
    prompt: string,
    agentConfig: any,
    conversationHistory: Message[] = []
  ) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('[WebSocket] Not connected');
      options.onError?.('WebSocket not connected. Trying to reconnect...');
      connect();
      return;
    }

    setIsLoading(true);
    
    const message = {
      type: 'run_agent',
      prompt,
      config: agentConfig,
      conversation_history: conversationHistory
    };

    console.log('[WebSocket] Sending message:', message);
    wsRef.current.send(JSON.stringify(message));
  }, [connect, options]);

  // Connect on mount with proper cleanup
  useEffect(() => {
    let mounted = true;
    
    // Only connect if mounted and not already connecting/connected
    if (mounted && !wsRef.current) {
      connect();
    }
    
    return () => {
      mounted = false;
      disconnect();
    };
  }, []); // Empty dependency array to run only once on mount

  return {
    isConnected,
    isLoading,
    sendMessage,
    connect,
    disconnect,
    sessionId
  };
}