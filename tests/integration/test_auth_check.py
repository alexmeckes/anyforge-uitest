from typing import TYPE_CHECKING

from streamlit.testing.v1 import AppTest

if TYPE_CHECKING:
    from any_forge.integrations import AuthStatus


def test_auth_check_authentication_status(any_forge_app: AppTest) -> None:
    """Test authentication checking Salesforce not authenticated."""
    any_forge_app.button(key="create_new_agent").click().run()
    any_forge_app.multiselect("integrations").set_value(["SALESFORCE"]).run()

    any_forge_app.button(key="check_credentials").click().run(timeout=120)
    any_forge_app.run(timeout=120)

    # Verify the authentication statuses are stored in session state
    assert "auth_statuses" in any_forge_app.session_state
    auth_statuses: list[AuthStatus] = any_forge_app.session_state["auth_statuses"]

    assert len(auth_statuses) == 1
    assert auth_statuses[0].integration == "SALESFORCE"
    assert not auth_statuses[0].is_authenticated
