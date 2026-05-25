"""Hand-tuned Union Jack patterns at the sizes used as flag/canton.

The patterns are encoded as character grids: '.' blue, 'W' white, 'R' red.
At 27x18 we include a stylized red counterchange. At canton sizes detail is
dropped — the goal is "reads as Union Jack" not full heraldic fidelity.
"""

from .palette import UK_BLUE, WHITE, UK_RED
from ._canvas import Canvas

_UJ_PAL = {".": UK_BLUE, "W": WHITE, "R": UK_RED}


# Full Union Jack at 27x18:
# - White saltire 2-3 px thick on both diagonals
# - 1-px red counterchange touching the inner side of each saltire arm
# - White cross of St George: x=11,15 vertical edges and y=7,10 horizontal edges
# - Red cross of St George: x=12,13,14 vertical core and y=8,9 horizontal core
UJ_27x18 = [
    "WWR........WRRRW........RWW",  # y=0
    ".WWR.......WRRRW.......RWW.",  # y=1
    "..WWR......WRRRW......RWW..",  # y=2
    "....WWR....WRRRW....RWW....",  # y=3
    ".....WWR...WRRRW...RWW.....",  # y=4
    "......WWWR.WRRRW.RWWW......",  # y=5
    "........WWWWRRRWWWW........",  # y=6
    "WWWWWWWWWWWWRRRWWWWWWWWWWWW",  # y=7  cross white top
    "RRRRRRRRRRRRRRRRRRRRRRRRRRR",  # y=8  cross red
    "RRRRRRRRRRRRRRRRRRRRRRRRRRR",  # y=9
    "WWWWWWWWWWWWRRRWWWWWWWWWWWW",  # y=10 cross white bottom
    "........WWWWRRRWWWW........",  # y=11
    "......WWWR.WRRRW.RWWW......",  # y=12
    ".....WWR...WRRRW...RWW.....",  # y=13
    "....WWR....WRRRW....RWW....",  # y=14
    "..WWR......WRRRW......RWW..",  # y=15
    ".WWR.......WRRRW.......RWW.",  # y=16
    "WWR........WRRRW........RWW",  # y=17
]

assert all(len(r) == 27 for r in UJ_27x18), [len(r) for r in UJ_27x18]
assert len(UJ_27x18) == 18


# Canton variant at 13x9: half the height of the 27x18 flag, just under half
# width — used for AU/NZ/Fiji/Tuvalu at 27x18 (canton sits at top-left).
# Simplified: white saltire, no red counterchange (too small).
UJ_CANTON_13x9 = [
    "W....WRW....W",  # y=0
    "..W..WRW..W..",  # y=1
    "....WWRWW....",  # y=2
    "WWWWWWWWWWWWW",  # y=3 cross white
    "RRRRRRRRRRRRR",  # y=4 cross red
    "WWWWWWWWWWWWW",  # y=5 cross white
    "....WWRWW....",  # y=6
    "..W..WRW..W..",  # y=7
    "W....WRW....W",  # y=8
]

assert all(len(r) == 13 for r in UJ_CANTON_13x9), [len(r) for r in UJ_CANTON_13x9]
assert len(UJ_CANTON_13x9) == 9


# Tiny 6x4 canton for the 13x9 small-flag variants (AU/NZ/Fiji/Tuvalu).
# At this size we just place a hint: blue with a red+white core. The goal is
# "this flag has a UK canton" — pixel-art accuracy isn't possible.
UJ_CANTON_6x4 = [
    "W.RR.W",
    "WWRRWW",
    "RRRRRR",
    "W.RR.W",
]
assert all(len(r) == 6 for r in UJ_CANTON_6x4)
assert len(UJ_CANTON_6x4) == 4


def stamp_union_jack_27x18(c: Canvas, x: int = 0, y: int = 0) -> None:
    c.stamp(x, y, UJ_27x18, _UJ_PAL)


def stamp_union_jack_canton_13x9(c: Canvas, x: int = 0, y: int = 0) -> None:
    c.stamp(x, y, UJ_CANTON_13x9, _UJ_PAL)


def stamp_union_jack_canton_6x4(c: Canvas, x: int = 0, y: int = 0) -> None:
    c.stamp(x, y, UJ_CANTON_6x4, _UJ_PAL)
