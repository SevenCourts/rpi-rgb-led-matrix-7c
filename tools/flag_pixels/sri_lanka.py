"""Sri Lanka — gold border, green/orange/maroon panels, lion holding sword.

Standard layout (left to right): two vertical panels (green + orange) take
about a third of the width; a maroon panel with a yellow lion and four
bo-leaves takes the rest. Outer gold border frames everything.
"""

from ._canvas import Canvas
from .palette import GOLD, DARK_GREEN, ORANGE, SAFFRON, MAROON, YELLOW


def large() -> Canvas:
    c = Canvas(27, 18, GOLD)
    # Inside the 1-px gold border: panels at x=1..25, y=1..16
    # Left half (green + saffron): cols 1..8 (8 cols)
    # Maroon area: cols 9..25 (17 cols)
    # Within left half: green 4 cols, saffron 4 cols
    c.rect(1, 1, 4, 16, DARK_GREEN)
    c.rect(5, 1, 8, 16, SAFFRON)
    c.rect(9, 1, 25, 16, MAROON)
    # Yellow lion (heraldic, facing left): blob silhouette suggesting a
    # crouched lion with raised paw holding a sword. At 9x10 px the shape
    # reads as "stylised animal with golden mane" against maroon — not
    # photographic, but distinctive enough that the flag isn't confused for
    # any other quartered design.
    lion = [
        "..YYY....",
        ".YYYYY...",
        ".YYY.....",
        "YYYYYY.Y.",  # body + sword (Y at x=7)
        "YYYYY..Y.",
        "YYYYYY.Y.",
        "Y.YY..YY.",
        "Y..Y..Y..",
        "Y..YY.Y..",
        "YY..YYY..",
    ]
    c.stamp(13, 3, lion, {"Y": YELLOW})
    # Four bo-leaves in corners of maroon panel (single yellow pixels)
    c.set(10, 2, YELLOW)
    c.set(24, 2, YELLOW)
    c.set(10, 15, YELLOW)
    c.set(24, 15, YELLOW)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, GOLD)
    # 1-px gold border; inside: panels at x=1..11, y=1..7
    # Left strip (green): 1..2 (2 cols)
    # Saffron: 3..4 (2 cols)
    # Maroon: 5..11 (7 cols)
    c.rect(1, 1, 2, 7, DARK_GREEN)
    c.rect(3, 1, 4, 7, SAFFRON)
    c.rect(5, 1, 11, 7, MAROON)
    # No lion at this size — just panels with the distinctive gold border
    return c
