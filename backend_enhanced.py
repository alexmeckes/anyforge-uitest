"""Enhanced backend with more features from Streamlit app."""
import sys
import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import asyncio
import tempfile
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import any-forge modules
from src.any_forge.state import AgentForgeAgent
from src.any_forge.storage import save_agents, load_agents
from src.any_forge.integrations import get_composio, check_authentication_status, SUPPORTED_INTEGRATIONS
from src.any_forge.generation.instructions import generate_instructions
from src.any_forge.generation.evaluation import generate_evaluation
from src.any_forge.generation.tools import get_recommended_tools

app = FastAPI(
    title="Any-Forge Enhanced API",
    description="Enhanced API with Composio integration and AI generation",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for development
development_agents: Dict[str, AgentForgeAgent] = {}
completed_agents: Dict[str, AgentForgeAgent] = {}

# Load existing agents on startup
try:
    dev_agents, comp_agents = load_agents()
    development_agents = dev_agents
    completed_agents = comp_agents
except:
    pass

# Composio instance (lazy loaded)
_composio = None

def get_composio_instance():
    """Get or create Composio instance."""
    global _composio
    if _composio is None:
        _composio = get_composio()
    return _composio


# --- Request/Response Models ---

class AgentCreateRequest(BaseModel):
    name: Optional[str] = None
    integrations: List[str] = []
    task_description: Optional[str] = None
    model_id: Optional[str] = None
    instructions: Optional[str] = None
    tools: List[str] = []
    evaluations: List[str] = []


class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    integrations: Optional[List[str]] = None
    task_description: Optional[str] = None
    model_id: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[str]] = None
    evaluations: Optional[List[str]] = None
    complete: Optional[bool] = None


class GenerateInstructionsRequest(BaseModel):
    task_description: str
    tools: List[str]


class GenerateEvaluationRequest(BaseModel):
    task_description: str
    tools: List[str]
    existing_evaluations: List[str] = []


class RecommendToolsRequest(BaseModel):
    task_description: str
    available_tools: List[str]


class ExecuteRequest(BaseModel):
    prompt: str
    conversation_history: List[Dict[str, str]] = []


# --- Helper Functions ---

def serialize_agent(agent: AgentForgeAgent) -> Dict[str, Any]:
    """Serialize agent to dict."""
    return {
        "id": agent.id,
        "name": agent.name,
        "integrations": agent.integrations,
        "task_description": agent.task_description,
        "model_id": agent.model_id,
        "instructions": agent.instructions,
        "tools": agent.tools,
        "evaluations": getattr(agent, 'evaluations', []),
        "complete": getattr(agent, 'complete', False),
        "created_at": agent.created_at.isoformat() if hasattr(agent, 'created_at') and agent.created_at else None,
        "updated_at": agent.updated_at.isoformat() if hasattr(agent, 'updated_at') and agent.updated_at else None,
        "traces_count": len(agent.traces) if hasattr(agent, 'traces') else 0
    }


# --- Agent CRUD Endpoints ---

@app.post("/api/agents")
async def create_agent(request: AgentCreateRequest):
    """Create a new agent."""
    agent = AgentForgeAgent(
        name=request.name,
        integrations=request.integrations,
        task_description=request.task_description,
        model_id=request.model_id,
        instructions=request.instructions,
        tools=request.tools,
        evaluations=request.evaluations
    )
    
    development_agents[agent.id] = agent
    save_agents(development_agents, completed_agents)
    
    return serialize_agent(agent)


@app.get("/api/agents")
async def list_agents(completed: Optional[bool] = None, page: int = 1, per_page: int = 20):
    """List all agents."""
    if completed is None:
        all_agents = list(development_agents.values()) + list(completed_agents.values())
    elif completed:
        all_agents = list(completed_agents.values())
    else:
        all_agents = list(development_agents.values())
    
    total = len(all_agents)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return {
        "agents": [serialize_agent(a) for a in all_agents[start_idx:end_idx]],
        "total": total,
        "page": page,
        "per_page": per_page
    }


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get a specific agent."""
    if agent_id in development_agents:
        return serialize_agent(development_agents[agent_id])
    elif agent_id in completed_agents:
        return serialize_agent(completed_agents[agent_id])
    else:
        raise HTTPException(status_code=404, detail="Agent not found")


@app.patch("/api/agents/{agent_id}")
async def update_agent(agent_id: str, request: AgentUpdateRequest):
    """Update an agent."""
    if agent_id in development_agents:
        agent = development_agents[agent_id]
    elif agent_id in completed_agents:
        agent = completed_agents[agent_id]
    else:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update fields
    if request.name is not None:
        agent.name = request.name
    if request.integrations is not None:
        agent.integrations = request.integrations
    if request.task_description is not None:
        agent.task_description = request.task_description
    if request.model_id is not None:
        agent.model_id = request.model_id
    if request.instructions is not None:
        agent.instructions = request.instructions
    if request.tools is not None:
        agent.tools = request.tools
    if request.evaluations is not None:
        agent.evaluations = request.evaluations
    
    # Handle completion status
    if request.complete is not None and request.complete != agent.complete:
        agent.complete = request.complete
        if request.complete:
            # Move to completed
            if agent_id in development_agents:
                del development_agents[agent_id]
                completed_agents[agent_id] = agent
        else:
            # Move to development
            if agent_id in completed_agents:
                del completed_agents[agent_id]
                development_agents[agent_id] = agent
    
    agent.updated_at = datetime.now()
    save_agents(development_agents, completed_agents)
    
    return serialize_agent(agent)


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent."""
    if agent_id in development_agents:
        del development_agents[agent_id]
        save_agents(development_agents, completed_agents)
        return {"success": True}
    elif agent_id in completed_agents:
        del completed_agents[agent_id]
        save_agents(development_agents, completed_agents)
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="Agent not found")


# --- Composio Integration Endpoints ---

@app.get("/api/integrations")
async def get_integrations():
    """Get all available integrations."""
    return {"integrations": SUPPORTED_INTEGRATIONS}

@app.get("/api/composio/integrations")
async def get_composio_integrations():
    """Get all available integrations (alternate endpoint)."""
    return {"integrations": SUPPORTED_INTEGRATIONS}


@app.get("/api/composio/auth-status/{integration}")
async def check_auth_status(integration: str, user_id: str = "default"):
    """Check authentication status for an integration."""
    try:
        composio = get_composio_instance()
        from any_forge.integrations import Integration, check_authentication_status, get_authentication_url
        
        # Check auth status
        statuses = check_authentication_status(composio, user_id, [Integration(integration)])
        status = statuses[0] if statuses else None
        
        response = {
            "integration": integration,
            "authenticated": status.is_authenticated if status else False,
            "status": "authenticated" if status and status.is_authenticated else "not_authenticated"
        }
        
        # Add auth URL if not authenticated
        if status and not status.is_authenticated:
            auth_url = get_authentication_url(composio, user_id, Integration(integration))
            if auth_url:
                response["auth_url"] = auth_url
        
        return response
    except Exception as e:
        return {
            "integration": integration,
            "authenticated": False,
            "status": "error",
            "error": str(e)
        }


class GetToolsRequest(BaseModel):
    integrations: List[str]
    limit: int = 500  # Increased to 500 with caching

# Simple in-memory cache for tools
tools_cache = {}

@app.post("/api/composio/tools")
async def get_tools(request: GetToolsRequest):
    """Get tools for specified integrations with caching."""
    # Create cache key from integrations and limit
    cache_key = f"{','.join(sorted(request.integrations))}_{request.limit}"
    
    # Check cache first
    if cache_key in tools_cache:
        return tools_cache[cache_key]
    
    try:
        composio = get_composio_instance()
        raw_tools = composio.tools.get_raw_composio_tools(
            toolkits=request.integrations,
            limit=request.limit
        )
        result = {
            "tools": [
                {"slug": tool.slug, "description": tool.description}
                for tool in raw_tools
            ]
        }
        
        # Cache the result
        tools_cache[cache_key] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- AI Generation Endpoints ---

@app.post("/api/generation/instructions")
async def generate_instructions_endpoint(request: GenerateInstructionsRequest):
    """Generate AI-powered instructions."""
    try:
        from any_agent.frameworks.tinyagent import DEFAULT_SYSTEM_PROMPT
        import asyncio
        
        print(f"[Instructions] Generating for task: {request.task_description[:100]}...")
        print(f"[Instructions] Tools: {request.tools}")
        
        # Run the sync function in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        gen_instructions = await loop.run_in_executor(
            None,
            generate_instructions,
            request.task_description,
            request.tools
        )
        
        print(f"[Instructions] Generated: {gen_instructions[:200]}...")
        
        # Format the full instructions like Streamlit does
        SPLIT_BEGINNING = "# Reminders"
        full_instructions = f"""{DEFAULT_SYSTEM_PROMPT}
{gen_instructions}
{SPLIT_BEGINNING}
- If a tool call fails with an error, don't try the same call again. Instead, try to understand the error and fix the root cause."""
        
        return {
            "instructions": full_instructions,
            "generated_part": gen_instructions  # Also return just the generated part for display
        }
    except Exception as e:
        # Fallback
        print(f"[Instructions] ERROR generating instructions: {e}")
        import traceback
        traceback.print_exc()
        
        from any_agent.frameworks.tinyagent import DEFAULT_SYSTEM_PROMPT
        fallback_gen = f"You are an AI assistant configured to help with: {request.task_description}"
        SPLIT_BEGINNING = "# Reminders"
        fallback_full = f"""{DEFAULT_SYSTEM_PROMPT}
{fallback_gen}
{SPLIT_BEGINNING}
- If a tool call fails with an error, don't try the same call again. Instead, try to understand the error and fix the root cause."""
        
        return {
            "instructions": fallback_full,
            "generated_part": fallback_gen
        }


@app.post("/api/generation/evaluation")
async def generate_evaluation_endpoint(request: GenerateEvaluationRequest):
    """Generate a new evaluation criterion."""
    try:
        evaluation = generate_evaluation(
            task_description=request.task_description,
            tools=request.tools,
            existing_evaluations=request.existing_evaluations
        )
        return {"evaluation": evaluation}
    except Exception as e:
        # Fallback
        return {
            "evaluation": f"The agent should successfully complete the task: {request.task_description}"
        }


@app.post("/api/generation/tools/recommend")
async def recommend_tools_endpoint(request: RecommendToolsRequest):
    """Get AI-recommended tools."""
    import time
    import asyncio
    start_time = time.time()
    
    print(f"[Tools] Recommending tools for task: {request.task_description[:50]}...")
    print(f"[Tools] Available tools count: {len(request.available_tools)}")
    
    try:
        # Run the sync function in a thread pool
        loop = asyncio.get_event_loop()
        recommended = await loop.run_in_executor(
            None,
            get_recommended_tools,
            request.task_description,
            request.available_tools
        )
        elapsed = time.time() - start_time
        print(f"[Tools] Recommended {len(recommended)} tools in {elapsed:.2f}s")
        return {"tools": recommended}
    except Exception as e:
        print(f"[Tools] Error recommending tools: {e}")
        # Fallback to first 5 tools
        return {"tools": request.available_tools[:5]}


# --- Agent Execution Endpoints ---

@app.post("/api/agents/{agent_id}/execute")
async def execute_agent(agent_id: str, request: ExecuteRequest):
    """Execute an agent (simplified for now)."""
    if agent_id in development_agents:
        agent = development_agents[agent_id]
    elif agent_id in completed_agents:
        agent = completed_agents[agent_id]
    else:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # This is a simplified execution - real implementation would use TinyAgent
    return {
        "success": True,
        "message": f"Agent would execute with prompt: {request.prompt}",
        "trace": {
            "messages": [
                {"role": "user", "content": request.prompt},
                {"role": "assistant", "content": "This is a simulated response"}
            ],
            "tool_calls": [],
            "outputs": ["Simulated output"],
            "metadata": {"execution_time": 0.1}
        }
    }


@app.post("/api/agents/{agent_id}/execute/stream")
async def stream_agent_execution(agent_id: str, request: ExecuteRequest):
    """Stream agent execution (simplified)."""
    if agent_id not in development_agents and agent_id not in completed_agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    async def generate():
        # Simulated streaming
        yield f"data: {json.dumps({'type': 'status', 'status': 'starting'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'type': 'output', 'content': 'Processing...'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'type': 'complete', 'trace': {}})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


# --- Agent Execution ---

class RunAgentRequest(BaseModel):
    prompt: str
    conversation_history: List[Dict[str, str]] = []
    # For temporary agents (when running without saving)
    agent_config: Optional[Dict[str, Any]] = None

@app.post("/api/agents/{agent_id}/run")
async def run_agent_endpoint(agent_id: str, request: RunAgentRequest):
    """Execute an agent with a prompt."""
    # Find the agent
    if agent_id in development_agents:
        agent = development_agents[agent_id]
    elif agent_id in completed_agents:
        agent = completed_agents[agent_id]
    else:
        # Try to create from request data if agent_id starts with "temp-"
        if agent_id.startswith("temp-") and request.agent_config:
            # Create a temporary agent from config
            from src.any_forge.state import AgentForgeAgent
            agent = AgentForgeAgent(
                id=agent_id,
                name=request.agent_config.get("name", "Temp Agent"),
                model_id=request.agent_config.get("model_id", "openai:gpt-4"),
                task_description=request.agent_config.get("task_description", ""),
                tools=request.agent_config.get("tools", []),
                instructions=request.agent_config.get("instructions", ""),
                integrations=request.agent_config.get("integrations", [])
            )
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        from src.any_forge.run import run_agent_async
        from src.any_forge.state import AgentForgeAgent
        from any_agent import AgentRunError
        
        # Set the prompt with conversation history if provided
        if request.conversation_history:
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.conversation_history])
            agent.prompt = f"Conversation history:\n{history_text}\n\nNew message: {request.prompt}"
        else:
            agent.prompt = request.prompt
        
        print(f"[Agent] Running agent {agent_id} with prompt: {request.prompt[:100]}...")
        
        # Run the agent
        result = await run_agent_async(agent)
        
        if isinstance(result, AgentRunError):
            print(f"[Agent] Error: {result}")
            return {
                "success": False,
                "error": str(result),
                "message": f"Error occurred: {result}",
                "trace": None
            }
        else:
            # Extract the final response from the trace
            final_message = "Agent completed the task successfully."
            
            # Debug: Let's see what the result contains
            print(f"[Agent] Result type: {type(result)}")
            print(f"[Agent] Result attributes: {dir(result)}")
            
            # Try different ways to extract the response
            if hasattr(result, 'output'):
                final_message = str(result.output)
                print(f"[Agent] Found output: {final_message[:200]}...")
            elif hasattr(result, 'result'):
                final_message = str(result.result)
                print(f"[Agent] Found result: {final_message[:200]}...")
            elif hasattr(result, 'messages') and result.messages:
                # Get the last assistant message
                for msg in reversed(result.messages):
                    if hasattr(msg, 'role') and msg.role == 'assistant':
                        final_message = msg.content if hasattr(msg, 'content') else str(msg)
                        print(f"[Agent] Found assistant message: {final_message[:200]}...")
                        break
            elif hasattr(result, 'spans') and result.spans:
                # Check spans for output
                for span in result.spans:
                    if hasattr(span, 'attributes'):
                        attrs = span.attributes
                        if 'gen_ai.output' in attrs:
                            final_message = str(attrs['gen_ai.output'])
                            print(f"[Agent] Found output in span: {final_message[:200]}...")
                            break
                        elif 'output' in attrs:
                            final_message = str(attrs['output'])
                            print(f"[Agent] Found output in span attributes: {final_message[:200]}...")
                            break
            
            print(f"[Agent] Final message: {final_message[:200]}...")
            
            # Store the trace
            agent.traces.append(result)
            
            return {
                "success": True,
                "message": final_message,
                "trace_index": len(agent.traces) - 1,
                "response": final_message  # Add for compatibility
            }
            
    except Exception as e:
        print(f"[Agent] Exception: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to run agent: {str(e)}"
        }

# --- WebSocket for Real-time Updates ---

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket for real-time agent updates (for future streaming support)."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back for now - will be enhanced for streaming
            await websocket.send_json({
                "type": "echo",
                "data": data,
                "agent_id": agent_id
            })
    except WebSocketDisconnect:
        pass


# --- Trace Management ---

@app.get("/api/agents/{agent_id}/traces")
async def get_agent_traces(agent_id: str):
    """Get traces for an agent."""
    if agent_id in development_agents:
        agent = development_agents[agent_id]
    elif agent_id in completed_agents:
        agent = completed_agents[agent_id]
    else:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Return simplified trace data
    return {
        "traces": [
            {
                "index": i,
                "timestamp": datetime.now().isoformat(),
                "messages": [],
                "outputs": []
            }
            for i in range(len(agent.traces))
        ]
    }


@app.get("/api/agents/{agent_id}/traces/download")
async def download_traces(agent_id: str):
    """Download agent traces as JSON."""
    if agent_id in development_agents:
        agent = development_agents[agent_id]
    elif agent_id in completed_agents:
        agent = completed_agents[agent_id]
    else:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    traces_data = {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "traces": []
    }
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(traces_data, f, indent=2)
        temp_path = f.name
    
    return FileResponse(
        path=temp_path,
        filename=f"agent_{agent_id}_traces.json",
        media_type="application/json"
    )


# --- Model Management ---

@app.get("/api/models")
async def get_models():
    """Get available AI models."""
    try:
        from any_llm import list_models
        
        # Get models from different providers
        models = []
        
        # OpenAI models
        openai_models = list_models("openai")
        for model in openai_models:
            models.append({
                "id": f"openai:{model.id}",
                "name": model.id,
                "provider": "OpenAI"
            })
        
        # Could add more providers here if needed
        # anthropic_models = list_models("anthropic")
        # for model in anthropic_models:
        #     models.append({
        #         "id": f"anthropic:{model.id}",
        #         "name": model.id,
        #         "provider": "Anthropic"
        #     })
        
        return {"models": models}
    except Exception as e:
        # Fallback to hardcoded list if any_llm fails
        return {
            "models": [
                {"id": "openai:gpt-4.1-mini", "name": "gpt-4.1-mini", "provider": "OpenAI"},
                {"id": "openai:gpt-4o", "name": "gpt-4o", "provider": "OpenAI"},
                {"id": "openai:gpt-4o-mini", "name": "gpt-4o-mini", "provider": "OpenAI"},
                {"id": "openai:gpt-4-turbo", "name": "gpt-4-turbo", "provider": "OpenAI"},
                {"id": "openai:gpt-4", "name": "gpt-4", "provider": "OpenAI"},
                {"id": "openai:gpt-3.5-turbo", "name": "gpt-3.5-turbo", "provider": "OpenAI"},
            ]
        }


# --- Health Check ---

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Any-Forge Enhanced API",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Agent CRUD with persistence",
            "Composio integration",
            "AI-powered generation",
            "Agent execution (simulated)",
            "WebSocket support",
            "Trace management"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check."""
    return {"status": "healthy", "service": "Any-Forge Enhanced API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False)