import nest_asyncio
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
nest_asyncio.apply()
st.set_page_config(page_title="Any-Forge", page_icon="🔨", layout="wide", initial_sidebar_state="expanded")

from app.agent_builder import agent_builder_page  # noqa: E402
from app.style import init_style  # noqa: E402

init_style()

agent_builder_page()
