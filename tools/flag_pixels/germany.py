"""Germany — black/red/gold horizontal tricolor.

The black stripe gets a 1-px dim border on top + left + right so the region
is visible against an LED panel background (panel-off pixels are pure black;
a flat (0,0,0) black stripe would be indistinguishable from "no flag").
Border colour matches the 18x12 source: (33, 33, 33).
"""

from ._canvas import Canvas

BLACK = (0, 0, 0)
BLACK_RIM = (33, 33, 33)
DE_RED = (221, 0, 0)
DE_GOLD = (255, 204, 0)


def large() -> Canvas:
    # 27x18: 6 black, 6 red, 6 gold
    c = Canvas(27, 18, BLACK)
    c.rect(0, 0, 26, 5, BLACK)
    c.rect(0, 6, 26, 11, DE_RED)
    c.rect(0, 12, 26, 17, DE_GOLD)
    # 1-px rim around the black stripe (top + sides; bottom meets red so no need)
    c.hline(0, 26, 0, BLACK_RIM)
    c.vline(0, 1, 5, BLACK_RIM)
    c.vline(26, 1, 5, BLACK_RIM)
    return c


def small() -> Canvas:
    # 13x9: 3 black, 3 red, 3 gold
    c = Canvas(13, 9, BLACK)
    c.rect(0, 0, 12, 2, BLACK)
    c.rect(0, 3, 12, 5, DE_RED)
    c.rect(0, 6, 12, 8, DE_GOLD)
    c.hline(0, 12, 0, BLACK_RIM)
    c.vline(0, 1, 2, BLACK_RIM)
    c.vline(12, 1, 2, BLACK_RIM)
    return c
