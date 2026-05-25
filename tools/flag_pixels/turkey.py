"""Turkey — red field with white crescent + 5-pointed star."""

from ._canvas import Canvas

TR_RED = (227, 10, 23)
WHITE = (255, 255, 255)


def _fill_disc(c: Canvas, cx: float, cy: float, r: float, color):
    for y in range(c.h):
        for x in range(c.w):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                c.set(x, y, color)


def large() -> Canvas:
    c = Canvas(27, 18, TR_RED)
    # Crescent: white disc, then red disc nudged right and slightly smaller
    # to bite a crescent shape. Centered around (10, 9).
    _fill_disc(c, 10, 9, 5.0, WHITE)
    _fill_disc(c, 12.5, 9, 4.2, TR_RED)
    # 5-pointed white star to the right of the crescent, centered ~(17, 9)
    star = [
        "..W..",
        ".WWW.",
        "WWWWW",
        ".W.W.",
        "W...W",
    ]
    c.stamp(15, 7, star, {"W": WHITE})
    return c


def small() -> Canvas:
    c = Canvas(13, 9, TR_RED)
    # Smaller crescent ~ center (5, 4), star ~ (10, 4)
    _fill_disc(c, 5, 4, 2.5, WHITE)
    _fill_disc(c, 6.5, 4, 2.0, TR_RED)
    # 3x3 star (just a plus + corners)
    star = [
        ".W.",
        "WWW",
        "W.W",
    ]
    c.stamp(9, 3, star, {"W": WHITE})
    return c
