"""Spain — red/yellow/red horizontal tricolor (1:2:1) with coat-of-arms hint."""

from ._canvas import Canvas
from .palette import SPAIN_YELLOW, SPAIN_RED, GOLD, BLACK, WHITE


def large() -> Canvas:
    c = Canvas(27, 18, SPAIN_YELLOW)
    # 1:2:1 = 4:10:4 vertically
    c.rect(0, 0, 26, 3, SPAIN_RED)
    c.rect(0, 14, 26, 17, SPAIN_RED)
    # Simplified coat of arms on the hoist side: two gold "Pillars of
    # Hercules" at cols 3 and 11, framing a gold-bordered red shield
    # (cols 5..9, rows 6..10). Crown hint above the shield.
    # Pillars
    c.vline(3, 5, 12, GOLD)
    c.vline(11, 5, 12, GOLD)
    # Crown above shield: 3 gold dots
    c.set(6, 5, GOLD)
    c.set(7, 5, GOLD)
    c.set(8, 5, GOLD)
    # Shield outline (gold)
    c.rect(5, 6, 9, 11, GOLD)
    # Shield interior (red)
    c.rect(6, 7, 8, 10, SPAIN_RED)
    # Tiny gold detail (quartering hint) — single pixel center
    c.set(7, 8, GOLD)
    c.set(7, 9, GOLD)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, SPAIN_YELLOW)
    # 1:2:1 = 2:5:2 vertically
    c.rect(0, 0, 12, 1, SPAIN_RED)
    c.rect(0, 7, 12, 8, SPAIN_RED)
    # No coat of arms at this size — tricolor reads cleanly
    return c
