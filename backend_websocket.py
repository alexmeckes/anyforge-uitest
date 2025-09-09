"""
WebSocket-enabled backend for real-time agent streaming.
Similar to how Streamlit uses callbacks, we'll stream responses as they happen.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import asyncio
from datetime import datetime
import traceback

# Import our existing backend modules
from src.any_forge.state import AgentForgeAgent
from src.any_forge.run import run_agent_async
from any_agent import AgentRunError
from any_agent.callbacks import Callback, Context
from any_agent.tracing.attributes import GenAI

app = FastAPI(title="Any-Forge WebSocket API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


class WebSocketCallback(Callback):
    """Callback to stream agent responses via WebSocket."""
    
    def __init__(self, websocket: WebSocket, session_id: str):
        """Initialize the WebSocket callback."""
        self.websocket = websocket
        self.session_id = session_id
        super().__init__()
    
    async def send_message(self, message_type: str, content: str, metadata: Dict = None):
        """Send a message through the WebSocket."""
        try:
            await self.websocket.send_json({
                "type": message_type,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"[WebSocket] Error sending message: {e}")
    
    def after_llm_call(self, context: Context, *args, **kwargs) -> Context:
        """Stream LLM responses."""
        try:
            span = context.current_span
            attributes = span.attributes
            output_value = str(attributes.get(GenAI.OUTPUT, ""))
            
            if output_value:
                # Send the LLM response immediately
                asyncio.create_task(self.send_message(
                    "assistant_message",
                    output_value,
                    {"source": "llm"}
                ))
                print(f"[WebSocket] Streaming LLM response: {output_value[:100]}...")
        except Exception as e:
            print(f"[WebSocket] Error in after_llm_call: {e}")
        
        return context
    
    def after_tool_execution(self, context: Context, *args, **kwargs) -> Context:
        """Stream tool execution results."""
        try:
            span = context.current_span
            attributes = span.attributes
            output_value = str(attributes.get(GenAI.OUTPUT, ""))
            tool_name = attributes.get("tool.name", "unknown")
            
            if output_value:
                # Send tool execution result
                asyncio.create_task(self.send_message(
                    "tool_execution",
                    output_value,
                    {"tool": tool_name, "source": "tool"}
                ))
                print(f"[WebSocket] Streaming tool execution ({tool_name}): {output_value[:100]}...")
        except Exception as e:
            print(f"[WebSocket] Error in after_tool_execution: {e}")
        
        return context


@app.websocket("/ws/agent/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time agent communication."""
    await websocket.accept()
    active_connections[session_id] = websocket
    print(f"[WebSocket] Client connected: {session_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "run_agent":
                await handle_agent_run(websocket, session_id, message)
            elif message["type"] == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Unknown message type: {message['type']}"
                })
                
    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected: {session_id}")
        if session_id in active_connections:
            del active_connections[session_id]
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        traceback.print_exc()
        if session_id in active_connections:
            del active_connections[session_id]


async def handle_agent_run(websocket: WebSocket, session_id: str, message: Dict):
    """Handle agent execution with real-time streaming."""
    try:
        config = message["config"]
        prompt = message["prompt"]
        conversation_history = message.get("conversation_history", [])
        
        # Send acknowledgment
        await websocket.send_json({
            "type": "status",
            "content": "Starting agent execution...",
            "metadata": {"status": "starting"}
        })
        
        # Create agent from config
        agent = AgentForgeAgent(
            id=f"ws-{session_id}",
            name=config.get("name", "WebSocket Agent"),
            model_id=config.get("model_id", "openai:gpt-4"),
            task_description=config.get("task_description", ""),
            tools=config.get("tools", []),
            instructions=config.get("instructions", ""),
            integrations=config.get("integrations", [])
        )
        
        # Set prompt with conversation history
        if conversation_history:
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history
            ])
            agent.prompt = f"Conversation history:\n{history_text}\n\nNew message: {prompt}"
        else:
            agent.prompt = prompt
        
        # Add WebSocket callback for streaming
        agent.callbacks = [WebSocketCallback(websocket, session_id)]
        
        print(f"[WebSocket] Running agent for session {session_id}")
        
        # Run the agent
        result = await run_agent_async(agent)
        
        if isinstance(result, AgentRunError):
            await websocket.send_json({
                "type": "error",
                "content": f"Agent error: {result}",
                "metadata": {"status": "error"}
            })
        else:
            # Send completion status
            await websocket.send_json({
                "type": "completion",
                "content": "Agent execution completed",
                "metadata": {"status": "completed"}
            })
            
    except Exception as e:
        print(f"[WebSocket] Error in handle_agent_run: {e}")
        traceback.print_exc()
        await websocket.send_json({
            "type": "error",
            "content": f"Error: {str(e)}",
            "metadata": {"status": "error"}
        })


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Any-Forge WebSocket API",
        "version": "1.0.0",
        "websocket_endpoint": "/ws/agent/{session_id}",
        "description": "Real-time agent streaming via WebSocket"
    }


@app.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "active_connections": len(active_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=False)