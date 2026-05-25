"""Finland — white field, blue Scandinavian cross."""

from ._scandinavian import scandi_cross_large, scandi_cross_small

FI_BLUE = (0, 53, 128)
WHITE = (255, 255, 255)


def large():
    return scandi_cross_large(WHITE, FI_BLUE)


def small():
    return scandi_cross_small(WHITE, FI_BLUE)
