"""Switzerland — red field + white Greek cross.

Switzerland's flag is square (1:1). On our 3:2 panels we don't stretch it:
the cross is drawn at square proportions and the panel has extra red on the
left/right. Canonical Swiss cross: arm thickness = L/6, half-length = 7L/30.
"""

from ._canvas import Canvas
from .palette import RED, WHITE


def large() -> Canvas:
    c = Canvas(27, 18, RED)
    # 18-tall square. Thickness=3, arms extend 4 px from center → 9 px total.
    # Centered at (13, 9).
    c.rect(12, 5, 14, 13, WHITE)   # vertical:   x=12..14, y=5..13
    c.rect(9, 8, 17, 10, WHITE)    # horizontal: x=9..17,  y=8..10
    return c


def small() -> Canvas:
    c = Canvas(13, 9, RED)
    # 9-tall square. Thickness=3, arms extend 3 px from center → 7 px total.
    # Centered at (6, 4).
    c.rect(5, 1, 7, 7, WHITE)      # vertical:   x=5..7, y=1..7
    c.rect(3, 3, 9, 5, WHITE)      # horizontal: x=3..9, y=3..5
    return c
