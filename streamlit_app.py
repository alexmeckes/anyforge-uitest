from enum import StrEnum

import nest_asyncio
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
nest_asyncio.apply()
st.set_page_config(page_title="Any-Forge", page_icon="🔨", layout="wide", initial_sidebar_state="expanded")

from app.agent_builder import agent_builder_page  # noqa: E402
from app.completed_agents import completed_agents_page  # noqa: E402
from app.style import init_style  # noqa: E402

init_style()


class Pages(StrEnum):
    """Pages of the app."""

    DEVELOP_AGENTS = "Develop Agents"
    COMPLETED_AGENTS = "Completed Agents"


page = st.sidebar.selectbox(
    "Navigate",
    [Pages.DEVELOP_AGENTS, Pages.COMPLETED_AGENTS],
    index=0,
)

if page == Pages.DEVELOP_AGENTS:
    agent_builder_page()
elif page == Pages.COMPLETED_AGENTS:
    completed_agents_page()
