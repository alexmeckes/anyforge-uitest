# This is designed as a single page web app (this single main page is designed to render all the other pages. Kind of a React-y design)

import streamlit as st

from any_forge.app.style import init_style
from any_forge.app.sub_pages.agent_build import agent_builder_page

st.set_page_config(page_title="Any-Forge", page_icon="🔨", layout="wide", initial_sidebar_state="expanded")

init_style()

agent_builder_page()
