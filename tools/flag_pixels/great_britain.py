"""Great Britain — full Union Jack."""

from ._canvas import Canvas
from .palette import UK_BLUE
from ._union_jack import (
    stamp_union_jack_27x18,
    stamp_union_jack_canton_13x9,
)


def large() -> Canvas:
    c = Canvas(27, 18, UK_BLUE)
    stamp_union_jack_27x18(c, 0, 0)
    return c


def small() -> Canvas:
    # 13x9 = canton size. Same pattern used as the canton on AU/NZ/Fiji/Tuvalu,
    # but here it IS the flag.
    c = Canvas(13, 9, UK_BLUE)
    stamp_union_jack_canton_13x9(c, 0, 0)
    return c
