"""Sweden — blue field, yellow Scandinavian cross."""

from ._canvas import Canvas

SE_BLUE = (0, 82, 147)
SE_YELLOW = (254, 204, 0)


def large() -> Canvas:
    c = Canvas(27, 18, SE_BLUE)
    # Cross: 3-wide vertical at hoist-offset (cols 8..10); 3-tall horizontal
    # centered vertically (rows 7..9). Proportions: 8 / 3 / 16 horizontal,
    # 7 / 3 / 8 vertical — approximates official 5:2:9 / 4:2:4 split.
    c.rect(8, 0, 10, 17, SE_YELLOW)
    c.rect(0, 7, 26, 9, SE_YELLOW)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, SE_BLUE)
    # 1-wide cross: vertical at col 4, horizontal at row 4
    c.vline(4, 0, 8, SE_YELLOW)
    c.hline(0, 12, 4, SE_YELLOW)
    return c
