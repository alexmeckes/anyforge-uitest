import streamlit as st
from models.state import AgentState

def init_session_state():
    if "current_step" not in st.session_state:
        st.session_state.current_step = AgentState.BUILD
