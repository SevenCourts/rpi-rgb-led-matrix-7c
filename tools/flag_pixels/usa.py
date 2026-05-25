"""USA — 9 visual stripes (collapsed from 13 for legibility) + blue canton.

13 official stripes don't fit cleanly into 18 px. We render 9 alternating
2-px stripes — the gestalt reads as the US flag at viewing distance.
Canton at top-hoist is solid blue with a scatter of single-px white stars
(real flag has 50 in a 5/6 alternating grid — impossible at this size).
"""

from ._canvas import Canvas

US_RED = (191, 10, 48)
US_BLUE = (10, 49, 97)
WHITE = (255, 255, 255)


def large() -> Canvas:
    c = Canvas(27, 18, WHITE)
    # 9 stripes of 2 px each, red on even-indexed stripes (0,2,4,6,8)
    for stripe in range(9):
        y0 = stripe * 2
        color = US_RED if stripe % 2 == 0 else WHITE
        c.rect(0, y0, 26, y0 + 1, color)
    # Canton: cols 0..10 (11 wide), rows 0..9 (10 tall) — covers 5 stripes
    c.rect(0, 0, 10, 9, US_BLUE)
    # White stars: 3 cols × 4 rows pattern in the canton, offset between rows
    for j, row_y in enumerate((1, 3, 5, 7)):
        offset = 0 if j % 2 == 0 else 1
        for col_x in range(2 + offset, 10, 2):
            c.set(col_x, row_y, WHITE)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, WHITE)
    # Alternate red/white per row
    for y in range(9):
        if y % 2 == 0:
            c.hline(0, 12, y, US_RED)
    # Canton: cols 0..4 (5 wide), rows 0..4 (5 tall)
    c.rect(0, 0, 4, 4, US_BLUE)
    # A few star pixels
    for (x, y) in [(1, 1), (3, 1), (1, 3), (3, 3), (2, 2)]:
        c.set(x, y, WHITE)
    return c
