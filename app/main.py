# This is designed as a single page web app (this single main page is designed to render all the other pages. Kind of a React-y design)

import streamlit as st
from style import init_style
from sub_pages.agent_build import agent_builder_page

st.set_page_config(page_title="Any-Forge", page_icon="🔨", layout="wide", initial_sidebar_state="expanded")

init_style()


def main() -> None:
    """Run the main page."""
    agent_builder_page()


if __name__ == "__main__":
    main()
