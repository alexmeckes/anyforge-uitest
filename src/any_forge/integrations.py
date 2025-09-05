import os
from enum import StrEnum

from any_agent.tools.composio import CallableProvider
from composio import Composio
from pydantic import BaseModel


# Full list of apps requested to be supported for Beta
class Integration(StrEnum):
    """Supported integrations."""

    SLACK = "SLACK"
    NOTION = "NOTION"
    SALESFORCE = "SALESFORCE"
    MONDAY = "MONDAY"
    JIRA = "JIRA"
    GITHUB = "GITHUB"
    CONFLUENCE = "CONFLUENCE"
    LINKEDIN = "LINKEDIN"
    # GREENHOUSE = "GREENHOUSE"  # Not supported by Composio yet. Made ticket https://github.com/ComposioHQ/composio/issues/1894
    GMAIL = "GMAIL"
    GOOGLE_SHEETS = "GOOGLESHEETS"
    GOOGLE_DOCS = "GOOGLEDOCS"
    GOOGLE_CALENDAR = "GOOGLECALENDAR"
    GOOGLE_DRIVE = "GOOGLEDRIVE"
    GOOGLE_MAPS = "GOOGLE_MAPS"
    CLICKUP = "CLICKUP"
    HUBSPOT = "HUBSPOT"
    LINEAR = "LINEAR"


SUPPORTED_INTEGRATIONS = list(Integration)


class AuthStatus(BaseModel):
    """Authentication status for an integration."""

    integration: str
    is_authenticated: bool
    error_message: str | None = None
    connection_id: str | None = None


def get_composio() -> Composio[CallableProvider]:
    """Get a Composio instance with the right provider."""
    return Composio(CallableProvider(), api_key=os.environ["COMPOSIO_API_KEY"])


def check_authentication_status(
    composio: Composio[CallableProvider], user_id: str, integrations: list[Integration]
) -> list[AuthStatus]:
    """Check authentication status for a list of integrations.

    Args:
        composio: Composio instance to use for API calls
        user_id: User ID to check authentication for
        integrations: List of integrations to check authentication for

    Returns:
        List of AuthStatus objects indicating authentication status for each integration

    """
    statuses = []
    for integration in integrations:
        # this is almost definitely not completely correct, but it's a step in the right direction I think
        connected_accounts = composio.connected_accounts.list(
            user_ids=[user_id], toolkit_slugs=[str(integration).upper()]
        )

        if any(account.status == "ACTIVE" for account in connected_accounts.items):
            statuses.append(
                AuthStatus(
                    integration=str(integration),
                    is_authenticated=True,
                )
            )
        else:
            statuses.append(
                AuthStatus(
                    integration=str(integration),
                    is_authenticated=False,
                    error_message=f"No active accounts found, account statuses: {[account.status for account in connected_accounts.items]}",
                )
            )
    return statuses


def get_authentication_url(composio: Composio[CallableProvider], user_id: str, integration: Integration) -> str | None:
    """Get authentication URL for an integration.

    Args:
        composio: Composio instance to use for API calls
        user_id: User ID to check authentication for
        integration: Integration to get authentication URL for

    Returns:
        Authentication URL or None if unable to generate

    """
    connection_request = composio.toolkits.authorize(user_id=user_id, toolkit=integration)
    return connection_request.redirect_url if connection_request.redirect_url else None
