import os

import pytest
from composio_client import BadRequestError, Composio

from any_forge.integrations import Integration, composio, user_id


def test_all_integration_enums_are_supported_toolkits() -> None:
    """Test that all Integration enum values correspond to supported Composio toolkits."""
    if composio is None or user_id is None:
        pytest.skip("COMPOSIO_API_KEY and COMPOSIO_USER_ID environment variables are not set")
    client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
    for integration in Integration:
        toolkit = client.toolkits.retrieve(slug=integration.value)
        assert toolkit is not None


def test_bad_enum_raises() -> None:
    """A bad enum should raise an error."""
    if composio is None or user_id is None:
        pytest.skip("COMPOSIO_API_KEY and COMPOSIO_USER_ID environment variables are not set")
    client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
    with pytest.raises(BadRequestError):
        client.toolkits.retrieve(slug="blah")
