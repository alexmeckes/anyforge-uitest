import json
import os
from typing import Any

from any_forge.state import AgentForgeAgent

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage")


def load_agents() -> tuple[dict[str, AgentForgeAgent], dict[str, AgentForgeAgent]]:
    """Load the agents from the database, returning (development_agents, completed_agents)."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    if not os.path.exists(os.path.join(STORAGE_DIR, "agents.json")):
        with open(os.path.join(STORAGE_DIR, "agents.json"), "w") as f:
            json.dump({}, f)
    with open(os.path.join(STORAGE_DIR, "agents.json")) as f:
        agents = json.load(f)

    all_agents = {agent_id: AgentForgeAgent.model_validate(agent) for agent_id, agent in agents.items()}

    development_agents = {agent_id: agent for agent_id, agent in all_agents.items() if not agent.complete}
    completed_agents = {agent_id: agent for agent_id, agent in all_agents.items() if agent.complete}

    return development_agents, completed_agents


def save_agents(development_agents: dict[str, AgentForgeAgent], completed_agents: dict[str, AgentForgeAgent]) -> None:
    """Save the agents to the database."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

    all_agents = {**development_agents, **completed_agents}
    agents_dict: dict[str, dict[str, Any]] = {
        agent.id: agent.model_dump(exclude={"callbacks"}) for agent in all_agents.values()
    }
    with open(os.path.join(STORAGE_DIR, "agents.json"), "w") as f:
        json.dump(agents_dict, f)
