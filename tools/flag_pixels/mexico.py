"""Mexico — green/white/red vertical tricolor with eagle hint at center."""

from ._canvas import Canvas
from .palette import MEXICO_GREEN, MEXICO_RED, WHITE, DARK_GREEN, BLACK, GOLD


def large() -> Canvas:
    c = Canvas(27, 18, WHITE)
    # Equal thirds: 9:9:9
    c.rect(0, 0, 8, 17, MEXICO_GREEN)
    c.rect(18, 0, 26, 17, MEXICO_RED)
    # Eagle on cactus (centre of white panel). At 5x7 we paint a small
    # eagle silhouette with wings spread and a thin snake/perch beneath.
    # Dark brown/green tones with a touch of red to suggest detail.
    eagle = [
        ".B.B.",   # wing tips
        "BBBBB",   # wings spread
        ".BBB.",   # body
        "..B..",   # tail
        "GGGGG",   # cactus / laurel base
        ".G.G.",   # base details
    ]
    c.stamp(11, 5, eagle, {"B": BLACK, "G": DARK_GREEN})
    # Snake hint — single gold pixel in the eagle's beak area
    c.set(13, 6, GOLD)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, WHITE)
    # Vertical thirds: 4:5:4
    c.rect(0, 0, 3, 8, MEXICO_GREEN)
    c.rect(8, 0, 12, 8, MEXICO_RED)
    # No coat of arms at this size — tricolor reads cleanly
    return c
