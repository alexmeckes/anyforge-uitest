import streamlit as st


def init_style():
    st.markdown(
        """
    <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .step-header {
            color: #2e7d32;
            border-bottom: 2px solid #2e7d32;
            padding-bottom: 0.5rem;
            margin: 1rem 0;
        }
        .agent-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #1f77b4;
            margin: 1rem 0;
        }
        .success-box {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
