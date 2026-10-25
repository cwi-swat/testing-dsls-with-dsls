"""Synchronous browser backend and session interfaces for miniTESTAR.

User-supplied functions receive the backend-specific browser object.
The session derives possible actions and executes the selected action.
"""
from typing import Any, Callable, Dict, List, Protocol

from actions import ActionResult


class BrowserSession(Protocol):
    """Describe what a browser session must provide, not how it works.

    This is a structural interface: a session such as PlaywrightSession
    satisfies it by providing the listed attribute and methods. Classes do not
    need to inherit from BrowserSession. A typechecker can check this;
    Python does not automatically validate the protocol at runtime.

    page is an instance attribute holding the backend-specific browser object.
    Currently this is a Playwright Page. Preparations, filters and oracles
    receive that object, so their code remains backend-specific.
    The annotations and ellipses below describe the interface only.
    """
    page: Any

    def close(self) -> None: ...
    def derive_actions(self, filters: List[Callable]) -> List[Dict[str, Any]]: ...
    def execute_action(self, action: Dict[str, Any], value=None) -> ActionResult: ...


class BrowserBackend(Protocol):
    """Describe a backend that starts the SUT and creates a browser session.

    Concrete backends satisfy this protocol by implementing start(), without
    needing to inherit from BrowserBackend.
    """
    def start(self, url: str) -> BrowserSession: ...
