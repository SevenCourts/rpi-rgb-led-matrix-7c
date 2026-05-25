"""Brazil — green field + yellow rhombus + blue celestial disc + banner."""

from ._canvas import Canvas
from .palette import BRAZIL_GREEN, BRAZIL_YELLOW, BRAZIL_BLUE, WHITE, BLACK


def large() -> Canvas:
    c = Canvas(27, 18, BRAZIL_GREEN)
    # Yellow rhombus — corners at (W/2, m), (W-m, H/2), (W/2, H-m), (m, H/2)
    # with m chosen so rhombus is large and clearly diamond-shaped.
    # Width 27, height 18; use center (13, 9), half-width 11, half-height 7.
    cx, cy = 13, 9
    hw, hh = 11, 7
    # Rasterize diamond: pixel (x, y) inside if |x-cx|/hw + |y-cy|/hh <= 1
    for y in range(18):
        for x in range(27):
            if abs(x - cx) / hw + abs(y - cy) / hh <= 1:
                c.set(x, y, BRAZIL_YELLOW)
    # Blue celestial disc — radius ~4 px centered at (13, 9)
    for y in range(18):
        for x in range(27):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 16:  # r=4
                c.set(x, y, BRAZIL_BLUE)
    # White banner across the disc — middle row of disc as white stripe
    c.hline(cx - 3, cx + 3, cy, WHITE)
    # A couple of white star pixels
    c.set(cx - 2, cy - 2, WHITE)
    c.set(cx + 2, cy - 1, WHITE)
    c.set(cx - 1, cy + 2, WHITE)
    c.set(cx + 1, cy + 2, WHITE)
    c.set(cx, cy - 3, WHITE)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, BRAZIL_GREEN)
    cx, cy = 6, 4
    hw, hh = 5, 3
    for y in range(9):
        for x in range(13):
            if abs(x - cx) / hw + abs(y - cy) / hh <= 1:
                c.set(x, y, BRAZIL_YELLOW)
    # Tiny blue disc 3x3
    c.rect(cx - 1, cy - 1, cx + 1, cy + 1, BRAZIL_BLUE)
    c.set(cx, cy, WHITE)
    return c
