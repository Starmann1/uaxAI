import pytest


def test_ui_importable():
    """Smoke test to verify that the Streamlit ui/app.py module is syntactically valid and importable."""
    try:
        # Import components from ui/app to verify no import/syntax errors
        from ui.app import MockLLMService
        assert MockLLMService is not None
    except Exception as e:
        pytest.fail(f"Failed to import from ui.app module: {e}")
