"""Shared Scandinavian-cross geometry — used by Denmark, Norway, Finland."""

from ._canvas import Canvas


def scandi_cross_large(field: tuple, cross: tuple) -> Canvas:
    c = Canvas(27, 18, field)
    c.rect(8, 0, 10, 17, cross)   # vertical bar (hoist-offset)
    c.rect(0, 7, 26, 9, cross)    # horizontal bar
    return c


def scandi_cross_small(field: tuple, cross: tuple) -> Canvas:
    c = Canvas(13, 9, field)
    c.vline(4, 0, 8, cross)
    c.hline(0, 12, 4, cross)
    return c
