import streamlit as st

from any_forge.generation.tools import get_recommended_tools
from any_forge.integrations import get_composio
from any_forge.state import AgentForgeAgent
from app.state import get_state


@st.cache_data
def _cached_get_all_tools(integrations: list[str]) -> list[dict[str, str]]:
    composio = get_composio()
    raw_tools = composio.tools.get_raw_composio_tools(toolkits=integrations, limit=1000)
    return [{"slug": t.slug, "description": t.description} for t in raw_tools]


@st.fragment
def render_tools(agent: AgentForgeAgent) -> None:
    """Render the tools step."""
    assert agent.task_description is not None
    st.subheader("Tools")
    if agent.tools:
        reselect_tools = st.button("Regenerate Tool Recommendation", key="regenerate_tools")
    else:
        reselect_tools = True
    all_tools = _cached_get_all_tools(agent.integrations)
    should_regenerate = get_state().should_regenerate_tools
    if reselect_tools or should_regenerate:
        with st.spinner("Generating tool selection..."):
            recommended_tool_names = get_recommended_tools(agent.task_description, [tool["slug"] for tool in all_tools])
            get_state().recommended_tool_names = recommended_tool_names
        get_state().should_regenerate_tools = False
    else:
        get_state().recommended_tool_names = agent.tools
    selected_tools: list[dict[str, str]] = st.multiselect(
        "Select tools to use:",
        options=all_tools,
        key="tools",
        default=[t for t in all_tools if t["slug"] in get_state().recommended_tool_names],
        format_func=lambda x: f"{x['slug']}: {x['description']}",
    )
    agent.tools = [t["slug"] for t in selected_tools]
