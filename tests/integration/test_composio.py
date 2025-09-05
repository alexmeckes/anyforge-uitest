import pytest
from composio_client import BadRequestError

from any_forge.integrations import Integration, get_composio


def test_all_integration_enums_are_supported_toolkits() -> None:
    """Test that all Integration enum values correspond to supported Composio toolkits."""
    try:
        cpo = get_composio()
    except KeyError:
        pytest.skip("COMPOSIO_API_KEY environment variable is not set")
    for integration in Integration:
        toolkit = cpo.toolkits.get(slug=integration.value)
        assert toolkit is not None


def test_bad_enum_raises() -> None:
    """A bad enum should raise an error."""
    try:
        cpo = get_composio()
    except KeyError:
        pytest.skip("COMPOSIO_API_KEY environment variable is not set")
    with pytest.raises(BadRequestError):
        cpo.toolkits.get(slug="blah")
