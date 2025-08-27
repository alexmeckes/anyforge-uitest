from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def any_forge_app() -> AppTest:
    app = AppTest.from_file(str(Path(__file__).parent.parent / "streamlit_app.py"))
    app.run(timeout=10)
    app.session_state["agents"] = {}
    return app
