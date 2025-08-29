import json
from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def any_forge_app() -> AppTest:
    app = AppTest.from_file(str(Path(__file__).parent.parent / "streamlit_app.py"))
    app.run(timeout=10)
    app.session_state["agents"] = {}
    return app


@pytest.fixture
def slack_tools_spec() -> list[dict[str, Any]]:
    """Load the Slack tools specification from JSON file."""
    spec_file = Path(__file__).parent / "assets" / "slack_tools_spec.json"
    with spec_file.open() as f:
        return json.load(f)  # type: ignore[no-any-return]
