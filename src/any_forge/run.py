from any_agent import AgentFramework, AgentRunError, AgentTrace, AnyAgent
from any_llm.utils.aio import run_async_in_sync

from any_forge.state import AgentForgeAgent


async def run_agent_async(forge_agent: AgentForgeAgent) -> AgentTrace | AgentRunError:
    """Run the agent."""
    forge_agent._check_fully_defined()

    config = forge_agent.get_agent_config()

    agent = await AnyAgent.create_async(agent_framework=AgentFramework.TINYAGENT, agent_config=config)

    prompt = forge_agent.get_prompt()

    kwargs = forge_agent.get_kwargs()
    try:
        trace: AgentTrace = await agent.run_async(prompt=prompt, **kwargs)
    except AgentRunError as e:
        return e

    return trace


def run_agent(forge_agent: AgentForgeAgent) -> AgentTrace | AgentRunError:
    """Run the agent."""
    return run_async_in_sync(run_agent_async(forge_agent))
