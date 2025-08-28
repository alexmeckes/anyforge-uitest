import nest_asyncio
import streamlit as st

from any_forge.app.agent_builder import agent_builder_page
from any_forge.app.style import init_style

nest_asyncio.apply()

st.set_page_config(page_title="Any-Forge", page_icon="🔨", layout="wide", initial_sidebar_state="expanded")

init_style()

agent_builder_page()
