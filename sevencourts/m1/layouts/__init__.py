"""Panel-type-aware Layout selection.

Use `current_layout()` to obtain the active Layout for the panel type configured
via the `PANEL_TYPE` env var (resolved at `dimens.py` import time).
"""

import os
from typing import Optional

from sevencourts.m1.layouts.types import (
    ClockLayout,
    ImageLayout,
    Layout,
    MessageLayout,
    ScoreboardLayout,
    SignageLayout,
)


_PANEL_TYPE = os.environ.get("PANEL_TYPE", "M1")
_cached: Optional[Layout] = None


def current_layout() -> Layout:
    """Return the Layout for the active panel type. Resolved lazily and cached."""
    global _cached
    if _cached is None:
        _cached = _resolve_layout()
    return _cached


def _resolve_layout() -> Layout:
    if _PANEL_TYPE == "M1":
        from sevencourts.m1.layouts.m1 import LAYOUT

        return LAYOUT
    if _PANEL_TYPE == "XL1":
        from sevencourts.m1.layouts.xl1 import LAYOUT

        return LAYOUT
    raise NotImplementedError(
        f"No Layout defined for PANEL_TYPE={_PANEL_TYPE!r}. "
        "Phase 3 will add the layout for L1."
    )


__all__ = [
    "ClockLayout",
    "ImageLayout",
    "Layout",
    "MessageLayout",
    "ScoreboardLayout",
    "SignageLayout",
    "current_layout",
]
