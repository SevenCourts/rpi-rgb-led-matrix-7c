"""South Korea — white field, Taegeuk (red/blue circle) + 4 black trigrams.

The real Taegeuk is an S-curve dividing red and blue halves of a disc; at
27×18 we can't render the curve so we just split the disc horizontally
(red top half / blue bottom half). The 4 trigrams sit in the corners.
"""

from ._canvas import Canvas

WHITE = (255, 255, 255)
KR_RED = (205, 46, 58)
KR_BLUE = (0, 56, 147)
BLACK = (10, 10, 10)


def large() -> Canvas:
    c = Canvas(27, 18, WHITE)
    # Taegeuk: disc radius 4 at center (13, 9)
    cx, cy, r2 = 13, 9, 16
    for y in range(18):
        for x in range(27):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                c.set(x, y, KR_RED if y < cy else KR_BLUE)
    # The center row needs to belong to one half; split it left=red / right=blue.
    for x in range(27):
        if (x - cx) ** 2 + 0 <= r2:
            c.set(x, cy, KR_RED if x <= cx else KR_BLUE)

    # Trigrams: 5x5 each, in the 4 corners.
    # Top-left ☰ Geon (heaven — 3 solid bars)
    c.stamp(0, 1, ["BBBBB", ".....", "BBBBB", ".....", "BBBBB"], {"B": BLACK})
    # Top-right ☵ Gam (water — solid, broken, solid)
    c.stamp(22, 1, ["BBBBB", ".....", "BB.BB", ".....", "BBBBB"], {"B": BLACK})
    # Bottom-left ☲ Ri (fire — broken, solid, broken)
    c.stamp(0, 12, ["BB.BB", ".....", "BBBBB", ".....", "BB.BB"], {"B": BLACK})
    # Bottom-right ☷ Gon (earth — 3 broken bars)
    c.stamp(22, 12, ["BB.BB", ".....", "BB.BB", ".....", "BB.BB"], {"B": BLACK})
    return c


def small() -> Canvas:
    c = Canvas(13, 9, WHITE)
    # Just the Taegeuk — no room for trigrams
    cx, cy, r2 = 6, 4, 6  # radius ≈ 2.45
    for y in range(9):
        for x in range(13):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                c.set(x, y, KR_RED if y < cy else KR_BLUE)
    for x in range(13):
        if (x - cx) ** 2 <= r2:
            c.set(x, cy, KR_RED if x <= cx else KR_BLUE)
    return c
