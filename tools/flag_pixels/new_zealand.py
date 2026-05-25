"""New Zealand — blue field + Union Jack canton + 4 red/white-bordered stars."""

from ._canvas import Canvas
from .palette import BLUE, WHITE, RED
from ._union_jack import (
    stamp_union_jack_canton_13x9,
    stamp_union_jack_canton_6x4,
)


def large() -> Canvas:
    c = Canvas(27, 18, BLUE)
    stamp_union_jack_canton_13x9(c, 0, 0)

    # 4 red stars with white border on the fly side (right half).
    # Each star: 3x3 plus of white with single red pixel at center.
    def star(cx: int, cy: int) -> None:
        c.set(cx, cy - 1, WHITE)
        c.set(cx - 1, cy, WHITE)
        c.set(cx + 1, cy, WHITE)
        c.set(cx, cy + 1, WHITE)
        c.set(cx, cy, RED)

    # Geographic positions on the real NZ flag (4 stars of the Southern Cross,
    # no epsilon):
    star(21, 3)   # alpha
    star(24, 8)   # beta
    star(17, 10)  # delta
    star(22, 14)  # gamma
    return c


def small() -> Canvas:
    c = Canvas(13, 9, BLUE)
    stamp_union_jack_canton_6x4(c, 0, 0)
    # 4 red dots on the fly side (no room for white borders)
    c.set(10, 1, RED)
    c.set(11, 5, RED)
    c.set(7, 6, RED)
    c.set(10, 7, RED)
    return c
