"""Shared setup for tests that use a real Chromium session."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'testar'))
from playwright_backend import PlaywrightBackend


def open_session(test):
    """Start an isolated browser and register cleanup, even if an assertion fails."""
    session = PlaywrightBackend(headless=True).start('about:blank')
    test.addCleanup(session.close)
    return session
