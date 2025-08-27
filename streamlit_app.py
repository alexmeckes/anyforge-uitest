import nest_asyncio
import streamlit as st

from any_forge.app.style import init_style
from any_forge.app.sub_pages.agent_build import agent_builder_page

nest_asyncio.apply()

st.set_page_config(page_title="Any-Forge", page_icon="🔨", layout="wide", initial_sidebar_state="expanded")

init_style()

agent_builder_page()
