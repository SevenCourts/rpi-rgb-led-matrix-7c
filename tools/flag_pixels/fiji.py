"""Fiji — light blue field + Union Jack canton + simplified shield."""

from ._canvas import Canvas
from .palette import LIGHT_BLUE, WHITE, RED, GOLD
from ._union_jack import (
    stamp_union_jack_canton_13x9,
    stamp_union_jack_canton_6x4,
)


def large() -> Canvas:
    c = Canvas(27, 18, LIGHT_BLUE)
    stamp_union_jack_canton_13x9(c, 0, 0)

    # Shield centered on the fly side (right half), about 6x8.
    # Top portion: red Cross of St George on white. Bottom portion: gold/red details.
    # We simplify to a recognizable white shield with a red cross.
    shield = [
        ".WWWWW.",
        "WWWWWWW",
        "WW.R.WW",
        "WRRRRRW",
        "WW.R.WW",
        "WW...WW",
        ".WWWWW.",
        "..WWW..",
    ]
    c.stamp(18, 6, shield, {"W": WHITE, "R": RED})
    return c


def small() -> Canvas:
    c = Canvas(13, 9, LIGHT_BLUE)
    stamp_union_jack_canton_6x4(c, 0, 0)
    # Tiny shield hint: 3x3 white with red cross center on the fly side
    shield = [
        "WWW",
        "WRW",
        "WWW",
    ]
    c.stamp(9, 4, shield, {"W": WHITE, "R": RED})
    return c
