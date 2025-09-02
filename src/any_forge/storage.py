import json
import os
from typing import Any

from any_forge.state import AgentForgeAgent

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage")


def load_agents() -> dict[str, AgentForgeAgent]:
    """Load the agents from the database."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    if not os.path.exists(os.path.join(STORAGE_DIR, "agents.json")):
        with open(os.path.join(STORAGE_DIR, "agents.json"), "w") as f:
            json.dump({}, f)
    with open(os.path.join(STORAGE_DIR, "agents.json")) as f:
        agents = json.load(f)
    return {agent_id: AgentForgeAgent.model_validate(agent) for agent_id, agent in agents.items()}


def save_agents(agents: dict[str, AgentForgeAgent]) -> None:
    """Save the agents to the database."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    agents_dict: dict[str, dict[str, Any]] = {
        agent.id: agent.model_dump(exclude={"callbacks"}) for agent in agents.values()
    }
    with open(os.path.join(STORAGE_DIR, "agents.json"), "w") as f:
        json.dump(agents_dict, f)
