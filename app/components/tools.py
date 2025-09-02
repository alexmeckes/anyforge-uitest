from typing import Any

import streamlit as st

from any_forge.generation.tools import get_recommended_tools, get_tool_schemas
from any_forge.state import AgentForgeAgent
from app.state import get_state


@st.cache_data
def _cached_get_all_tool_schemas(integrations: list[str]) -> list[dict[str, Any]]:
    return get_tool_schemas(integrations)


@st.fragment
def render_tools(agent: AgentForgeAgent) -> None:
    """Render the tools step."""
    assert agent.task_description is not None
    st.subheader("Tools")
    if agent.tools:
        reselect_tools = st.button("Regenerate Tool Recommendation", key="regenerate_tools")
    else:
        reselect_tools = True
    all_tools = _cached_get_all_tool_schemas(agent.integrations)
    should_regenerate = get_state().should_regenerate_tools
    if reselect_tools or should_regenerate:
        with st.spinner("Generating tool selection..."):
            recommended_tool_names = get_recommended_tools(agent.task_description, all_tools)
            get_state().recommended_tool_names = recommended_tool_names
        get_state().should_regenerate_tools = False
    else:
        get_state().recommended_tool_names = [x["function"]["name"] for x in agent.tools]
    selected_tools: list[dict[str, Any]] = st.multiselect(
        "Select tools to use:",
        options=all_tools,
        key="tools",
        default=[x for x in all_tools if x["function"]["name"] in get_state().recommended_tool_names],
        format_func=lambda x: f"{x['function']['name']}: {x['function']['description']}",
    )
    agent.tools = selected_tools
