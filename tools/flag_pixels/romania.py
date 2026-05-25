"""Romania — blue/yellow/red vertical tricolor (equal thirds)."""

from ._canvas import Canvas

RO_BLUE = (0, 43, 127)
RO_YELLOW = (252, 209, 22)
RO_RED = (206, 17, 38)


def large() -> Canvas:
    c = Canvas(27, 18, RO_YELLOW)
    c.rect(0, 0, 8, 17, RO_BLUE)
    c.rect(18, 0, 26, 17, RO_RED)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, RO_YELLOW)
    # Equal thirds at 13 wide ≈ 4/5/4
    c.rect(0, 0, 3, 8, RO_BLUE)
    c.rect(9, 0, 12, 8, RO_RED)
    return c
