"""Argentina — light-blue/white/light-blue horizontal tricolor + Sun of May."""

from ._canvas import Canvas
from .palette import ARGENTINA_BLUE, WHITE, ARGENTINA_SUN, GOLD


def large() -> Canvas:
    c = Canvas(27, 18, WHITE)
    # Equal-thirds: 6:6:6 vertically
    c.rect(0, 0, 26, 5, ARGENTINA_BLUE)
    c.rect(0, 12, 26, 17, ARGENTINA_BLUE)
    # Sun of May — gold disc with rays at center (13, 9)
    cx, cy = 13, 9
    # 3x3 disc core
    c.rect(cx - 1, cy - 1, cx + 1, cy + 1, ARGENTINA_SUN)
    # 8 rays (N S E W + diagonals), 1 px each, 1 px gap from disc
    c.set(cx, cy - 3, ARGENTINA_SUN)
    c.set(cx, cy + 3, ARGENTINA_SUN)
    c.set(cx - 3, cy, ARGENTINA_SUN)
    c.set(cx + 3, cy, ARGENTINA_SUN)
    c.set(cx - 2, cy - 2, ARGENTINA_SUN)
    c.set(cx + 2, cy - 2, ARGENTINA_SUN)
    c.set(cx - 2, cy + 2, ARGENTINA_SUN)
    c.set(cx + 2, cy + 2, ARGENTINA_SUN)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, WHITE)
    # 3:3:3 vertically
    c.rect(0, 0, 12, 2, ARGENTINA_BLUE)
    c.rect(0, 6, 12, 8, ARGENTINA_BLUE)
    # Tiny sun: single gold pixel at center
    c.set(6, 4, ARGENTINA_SUN)
    return c
