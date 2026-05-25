"""Denmark — red field, white Scandinavian cross (Dannebrog)."""

from ._scandinavian import scandi_cross_large, scandi_cross_small

DK_RED = (200, 16, 46)
WHITE = (255, 255, 255)


def large():
    return scandi_cross_large(DK_RED, WHITE)


def small():
    return scandi_cross_small(DK_RED, WHITE)
