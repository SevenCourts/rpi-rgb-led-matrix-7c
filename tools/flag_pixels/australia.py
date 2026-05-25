"""Australia — blue field + Union Jack canton + Federation star + Southern Cross."""

from ._canvas import Canvas
from .palette import BLUE, WHITE
from ._union_jack import (
    stamp_union_jack_canton_13x9,
    stamp_union_jack_canton_6x4,
)


def large() -> Canvas:
    c = Canvas(27, 18, BLUE)
    # Union Jack canton top-left, 13x9
    stamp_union_jack_canton_13x9(c, 0, 0)
    # Federation (Commonwealth) star — 7-pointed, sits below the canton, hoist side
    # 5x5 stylized star at (3..7, 11..15)
    fed_star = [
        "..W..",
        ".WWW.",
        "WWWWW",
        ".WWW.",
        ".W.W.",
    ]
    c.stamp(3, 11, fed_star, {"W": WHITE})

    # Southern Cross — 5 stars in the fly half (right half).
    # Real constellation: alpha (top-right), beta (centre), gamma (lower-left of beta),
    # delta (upper-left of beta), epsilon (small, between beta and gamma).
    # Each big star: 3x3 plus shape. Epsilon: single pixel.

    def big_star(cx: int, cy: int) -> None:
        c.set(cx, cy - 1, WHITE)
        c.set(cx - 1, cy, WHITE)
        c.set(cx, cy, WHITE)
        c.set(cx + 1, cy, WHITE)
        c.set(cx, cy + 1, WHITE)

    big_star(22, 2)   # Alpha — top
    big_star(24, 8)   # Beta — middle right
    big_star(17, 9)   # Delta — middle left
    big_star(22, 14)  # Gamma — bottom
    c.set(20, 12, WHITE)  # Epsilon — small
    return c


def small() -> Canvas:
    c = Canvas(13, 9, BLUE)
    # 6x4 canton at top-left
    stamp_union_jack_canton_6x4(c, 0, 0)
    # Federation star below canton — single white pixel (no room for a shape)
    c.set(2, 6, WHITE)
    # Southern Cross — 4 stars on the right half (drop epsilon)
    c.set(10, 1, WHITE)  # alpha
    c.set(11, 5, WHITE)  # beta
    c.set(7, 6, WHITE)   # delta
    c.set(10, 7, WHITE)  # gamma
    return c
