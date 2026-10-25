"""Action results and exceptions shared by TESTAR and browser implementations."""
from dataclasses import dataclass
from typing import Literal, Optional


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
