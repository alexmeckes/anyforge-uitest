# This is designed as a single page web app (this single main page is designed to render all the other pages. Kind of a React-y design)

import streamlit as st
from style import init_style
from sub_pages.agent_build import agent_builder_page
from sub_pages.agent_run import agent_run_page
from models.state import AgentState
from components.state import init_session_state

st.set_page_config(page_title="Any-Forge", page_icon="🔨", layout="wide", initial_sidebar_state="expanded")

init_style()

def main():

    init_session_state()

    st.write("Any-Forge")
    st.write("---")

    with st.sidebar:
        st.markdown("### Navigation")

        steps = {
            AgentState.BUILD: "Build",
            AgentState.RUN: "Run",
        }

        for step_key, step_name in steps.items():
            if st.button(step_name, key=f"nav_{step_key}", use_container_width=True):
                st.session_state.current_step = step_key
                st.rerun()


    current_step = st.session_state.current_step

    if current_step == AgentState.BUILD:
        agent_builder_page()
    elif current_step == AgentState.RUN:
        agent_run_page()


if __name__ == "__main__":
    main()
