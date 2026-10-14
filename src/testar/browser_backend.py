"""Synchronous browser backend and session interfaces for miniTESTAR.

User-supplied functions receive the backend-specific browser object.
The session derives action descriptions and executes the selected description.
"""
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Literal, Optional, Protocol


@dataclass(frozen=True)
class ActionResult:
    """Outcome of one attempt, not proof of the application's correctness.

    execution_succeeded means browser calls completed, not proof of SUT correctness.
    execution_skipped means the intended action did not begin (scrolling may have run).
    execution_failed means effects may be partial; never automatically replay it.
    Error details are plain strings so future traces can store them.
    """
    status: Literal['execution_succeeded', 'execution_skipped', 'execution_failed']
    error: Optional[str] = None
    error_type: Optional[str] = None


class ActionNotReachable(Exception):
    """The target is blocked or disabled; no action has been executed.

    A reachability check may already have scrolled the page. The core skips
    this target's remaining descriptions and tries another candidate.
    """


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
    actionable_element_count: int

    def close(self) -> None: ...
    def derive_actionable_elements(self, filters: List[Callable]) -> List[Any]: ...
    def get_element_info(self, element: Any) -> Dict[str, Any]: ...
    def derive_actions(self, filters: List[Callable]) -> List[Dict[str, Any]]: ...
    def derive_action_descriptions(self, elements: List[Any]) -> List[Dict[str, Any]]: ...
    def execute_action_description(self, description: Dict[str, Any], value=None) -> ActionResult: ...


class BrowserBackend(Protocol):
    """Describe a backend that starts the SUT and creates a browser session.

    Concrete backends satisfy this protocol by implementing start(), without
    needing to inherit from BrowserBackend.
    """
    def start(self, url: str) -> BrowserSession: ...
