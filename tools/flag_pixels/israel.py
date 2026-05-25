"""Israel — white field with two blue stripes and Star of David."""

from ._canvas import Canvas

WHITE = (255, 255, 255)
IL_BLUE = (0, 56, 184)


def large() -> Canvas:
    c = Canvas(27, 18, WHITE)
    # Blue stripes
    c.rect(0, 2, 26, 3, IL_BLUE)
    c.rect(0, 14, 26, 15, IL_BLUE)
    # Star of David — two overlapping triangles drawn as outline (9x9 hexagram)
    star = [
        "....X....",
        "...X.X...",
        "..X...X..",
        "XXXXXXXXX",
        ".X.....X.",
        "XXXXXXXXX",
        "..X...X..",
        "...X.X...",
        "....X....",
    ]
    c.stamp(9, 5, star, {"X": IL_BLUE})
    return c


def small() -> Canvas:
    c = Canvas(13, 9, WHITE)
    # 1-px stripes at top + bottom
    c.hline(0, 12, 1, IL_BLUE)
    c.hline(0, 12, 7, IL_BLUE)
    # 5x5 stylized star at center
    star = [
        "..X..",
        ".X.X.",
        "XXXXX",
        ".X.X.",
        "..X..",
    ]
    c.stamp(4, 2, star, {"X": IL_BLUE})
    return c
