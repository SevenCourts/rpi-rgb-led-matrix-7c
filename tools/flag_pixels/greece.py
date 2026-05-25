"""Greece — 9 blue/white horizontal stripes + blue canton with white cross.

Canton is square (5 stripes tall × ~5 stripes wide) per the official 2:3 spec.
On our 27x18 panel each stripe is 2 px tall, so 9 stripes = 18 rows exactly.
"""

from ._canvas import Canvas

GR_BLUE = (0, 70, 160)
WHITE = (255, 255, 255)


def large() -> Canvas:
    c = Canvas(27, 18, WHITE)
    # 9 stripes of 2 rows each, alternating blue/white (starting with blue).
    for stripe in range(9):
        if stripe % 2 == 0:
            c.rect(0, stripe * 2, 26, stripe * 2 + 1, GR_BLUE)
    # Canton: 10 px wide × 10 px tall at the top-hoist (cols 0..9, rows 0..9)
    c.rect(0, 0, 9, 9, GR_BLUE)
    # Bold white cross inside the canton: 3-px arms spanning the full canton.
    c.rect(3, 0, 5, 9, WHITE)   # vertical:   cols 3..5, full height
    c.rect(0, 3, 9, 5, WHITE)   # horizontal: rows 3..5, full width
    return c


def small() -> Canvas:
    c = Canvas(13, 9, WHITE)
    # 9 stripes of 1 row each at this scale
    for stripe in range(9):
        if stripe % 2 == 0:
            c.hline(0, 12, stripe, GR_BLUE)
    # Canton: 5 × 5 at top-hoist; white cross with 1-px arms
    c.rect(0, 0, 4, 4, GR_BLUE)
    c.vline(2, 0, 4, WHITE)
    c.hline(0, 4, 2, WHITE)
    return c
