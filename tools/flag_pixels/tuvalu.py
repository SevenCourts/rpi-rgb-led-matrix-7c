"""Tuvalu — light blue field + Union Jack canton + 9 yellow stars (islands)."""

from ._canvas import Canvas
from .palette import LIGHT_BLUE, YELLOW, GOLD
from ._union_jack import (
    stamp_union_jack_canton_13x9,
    stamp_union_jack_canton_6x4,
)


def large() -> Canvas:
    c = Canvas(27, 18, LIGHT_BLUE)
    stamp_union_jack_canton_13x9(c, 0, 0)

    # 9 yellow stars in the fly half (right of canton) and below it (fly half lower)
    # Real flag arrangement roughly traces the geographic positions of the 9 islands;
    # we approximate as scattered points. Each star is a single yellow pixel.
    star_positions = [
        (16, 2),
        (20, 1),
        (24, 4),
        (16, 6),
        (22, 7),
        (26, 9),
        (18, 11),
        (23, 13),
        (20, 16),
    ]
    for x, y in star_positions:
        c.set(x, y, YELLOW)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, LIGHT_BLUE)
    stamp_union_jack_canton_6x4(c, 0, 0)
    # Fewer dots at small size — keep 5 representative stars on the fly side
    dots = [(8, 1), (11, 2), (10, 5), (8, 7), (12, 7)]
    for x, y in dots:
        c.set(x, y, YELLOW)
    return c
