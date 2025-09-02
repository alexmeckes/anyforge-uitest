import streamlit as st

from any_forge.integrations import AuthStatus, Integration, check_authentication_status, get_authentication_url
from any_forge.state import AgentForgeAgent


def render_auth_check(agent: AgentForgeAgent) -> None:
    """Render authentication status checking component."""
    if st.button("Check Credentials", type="secondary", key="check_credentials"):
        integrations = [Integration(integration) for integration in agent.integrations]
        st.session_state["auth_statuses"] = check_authentication_status(integrations)

    if "auth_statuses" in st.session_state:
        auth_statuses: list[AuthStatus] = st.session_state["auth_statuses"]

        authenticated_count = sum(1 for status in auth_statuses if status.is_authenticated)
        total_count = len(auth_statuses)

        if authenticated_count == total_count:
            st.success(f"✅ All {total_count} integrations are authenticated!")
        elif authenticated_count == 0:
            st.error(f"❌ None of the {total_count} integrations are authenticated.")
        else:
            st.warning(f"⚠️ {authenticated_count}/{total_count} integrations are authenticated.")

        st.divider()

        for status in auth_statuses:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 2])

                with col1:
                    st.write(f"**{status.integration}**")

                with col2:
                    if status.is_authenticated:
                        st.success("✅ Connected")
                    else:
                        st.error("❌ Not Connected")

                with col3:
                    if not status.is_authenticated:
                        if status.error_message:
                            st.caption(f"Error: {status.error_message}")

                        auth_url = get_authentication_url(Integration(status.integration))
                        if auth_url:
                            st.link_button("Authenticate", auth_url, help="Click to authenticate with this service")
                        else:
                            st.caption("Unable to generate authentication URL")
                    else:
                        if status.connection_id:
                            st.caption(f"Connection ID: {status.connection_id[:8]}...")

                st.divider()
