import inspect
import os
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from composio import Composio
from composio.core.provider._openai import OpenAIProvider
from pydantic import BaseModel

composio_api_key = os.getenv("COMPOSIO_API_KEY")
_user_id = os.getenv("COMPOSIO_USER_ID")
user_id: str | None = None
composio: Composio[OpenAIProvider] | None = None
if composio_api_key and _user_id:
    user_id = str(_user_id)
    composio = Composio(api_key=composio_api_key)


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


def check_authentication_status(integrations: list[Integration]) -> list[AuthStatus]:
    """Check authentication status for a list of integrations.

    Args:
        integrations: List of integrations to check authentication for

    Returns:
        List of AuthStatus objects indicating authentication status for each integration

    """
    if composio is None or user_id is None:
        err_msg = "COMPOSIO_API_KEY and COMPOSIO_USER_ID environment variables are not set"
        raise ValueError(err_msg)

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


def get_authentication_url(integration: Integration) -> str | None:
    """Get authentication URL for an integration.

    Args:
        integration: Integration to get authentication URL for

    Returns:
        Authentication URL or None if unable to generate

    """
    if composio is None or user_id is None:
        msg = "COMPOSIO_API_KEY and COMPOSIO_USER_ID environment variables are not set"
        raise ValueError(msg)

    connection_request = composio.toolkits.authorize(user_id=user_id, toolkit=integration)
    return connection_request.redirect_url if connection_request.redirect_url else None


def get_integrations(integrations: list[Integration]) -> dict[str, list[dict[str, Any]]]:
    """Get wrapped Composio tools as callables for each supported app.

    Returns:
        Dictionary mapping app names to lists of callable tool functions

    """
    if composio is None or user_id is None:
        err_msg = "COMPOSIO_API_KEY and COMPOSIO_USER_ID environment variables are not set"
        raise ValueError(err_msg)

    tools: dict[str, list[dict[str, Any]]] = {}
    for app in integrations:
        toolkit = composio.tools.get(user_id=user_id, toolkits=[app], limit=1000)
        if toolkit:
            tools[str(app)] = toolkit
        else:
            tools[str(app)] = []
    return tools


def create_tool_callable(tool_schema: dict[str, Any]) -> Callable[..., Any]:
    """Create a callable function from a Composio tool schema."""
    name = tool_schema.get("name")
    if not name:
        msg = "Name is required"
        raise ValueError(msg)

    description = tool_schema.get("description")
    if not description:
        msg = "Description is required"
        raise ValueError(msg)

    parameters_schema = tool_schema.get("parameters")
    if not parameters_schema:
        msg = "Parameters are required"
        raise ValueError(msg)

    # Type mapping for JSON schema to Python types
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }

    def json_schema_to_python_type(schema: dict[str, Any]) -> type:
        """Convert JSON schema to Python type."""
        schema_type = schema.get("type", "string")  # fallback is to stry
        return type_mapping.get(schema_type, str)

    parameters = []
    annotations = {}
    param_descriptions = {}
    if parameters_schema and isinstance(parameters_schema, dict):
        properties = parameters_schema.get("properties", {})
        required = parameters_schema.get("required", [])

        for param_name, param_info in properties.items():
            base_param_type = json_schema_to_python_type(param_info)

            param_descriptions[param_name] = param_info.get("description", f"Parameter {param_name}")

            if param_name not in required:
                optional_param_type: Any = base_param_type | None
                annotations[param_name] = optional_param_type
                param = inspect.Parameter(
                    param_name,
                    inspect.Parameter.KEYWORD_ONLY,
                    default=None,
                    annotation=optional_param_type,
                )
            else:
                # Required parameter
                required_param_type: Any = base_param_type
                annotations[param_name] = required_param_type
                param = inspect.Parameter(
                    param_name,
                    inspect.Parameter.KEYWORD_ONLY,
                    annotation=required_param_type,
                )
            parameters.append(param)

    signature = inspect.Signature(parameters, return_annotation=dict)

    def composio_tool_function(**kwargs: Any) -> dict[str, Any]:
        """Dynamically created Composio tool function."""
        if composio is None or user_id is None:
            msg = "COMPOSIO_API_KEY and COMPOSIO_USER_ID environment variables are not set"
            raise ValueError(msg)

        result: dict[str, Any] = composio.tools.execute(name, user_id=user_id, arguments=kwargs)  # type: ignore[assignment]

        if not result.get("successful"):
            raise ValueError(result.get("error"))

        data: dict[str, Any] | None = result.get("data")
        if not data:
            msg = "No response returned from Composio"
            raise ValueError(msg)

        return data

    composio_tool_function.__name__ = name
    composio_tool_function.__doc__ = description
    composio_tool_function.__signature__ = signature  # type: ignore[attr-defined]
    composio_tool_function.__annotations__ = {**annotations, "return": dict}

    return composio_tool_function
