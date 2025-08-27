from any_agent import AgentFramework, AgentTrace, AnyAgent
from any_llm.utils.aio import run_async_in_sync

from any_forge.state import AgentCreationState, AgentForgeAgent


async def run_agent_async(forge_agent: AgentForgeAgent) -> AgentTrace:
    """Run the agent."""
    if forge_agent.state_machine.state not in [AgentCreationState.REVIEW, AgentCreationState.COMPLETE]:
        msg = f"Agent is not available to run: state is {forge_agent.state_machine.state}"
        raise ValueError(msg)

    config = forge_agent.get_agent_config()

    agent = await AnyAgent.create_async(agent_framework=AgentFramework.TINYAGENT, agent_config=config)

    prompt = forge_agent.get_prompt()

    kwargs = forge_agent.get_kwargs()

    # To handle the trace as it happens, the agent should have a callback added to the AgentConfig where the calling application can log/save/monitor etc.
    # This trace is the final trace and useful for saving final results etc.
    trace: AgentTrace = await agent.run_async(prompt=prompt, **kwargs)

    return trace


def run_agent(forge_agent: AgentForgeAgent) -> AgentTrace:
    """Run the agent."""
    return run_async_in_sync(run_agent_async(forge_agent))
