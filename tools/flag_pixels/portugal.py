"""Portugal — green/red vertical bicolor (2:3 split) + armillary sphere + shield hint."""

from ._canvas import Canvas
from .palette import PORTUGAL_GREEN, PORTUGAL_RED, GOLD, WHITE, YELLOW, BLACK


def large() -> Canvas:
    c = Canvas(27, 18, PORTUGAL_RED)
    # 2:3 split → green is 2/5 of 27 ≈ 11 cols (0..10), red 11..26
    c.rect(0, 0, 10, 17, PORTUGAL_GREEN)
    # Armillary sphere at the split, vertically centered
    # Sphere = small yellow circle 7x7 centered at (10, 9)
    sphere_cx, sphere_cy = 10, 9
    sphere = [
        "..YYY..",
        ".YYYYY.",
        "YYYYYYY",
        "YYYYYYY",
        "YYYYYYY",
        ".YYYYY.",
        "..YYY..",
    ]
    pal = {"Y": GOLD}
    c.stamp(sphere_cx - 3, sphere_cy - 3, sphere, pal)
    # Equator band (horizontal stripe through sphere)
    c.hline(sphere_cx - 3, sphere_cx + 3, sphere_cy, PORTUGAL_RED)
    # Shield (white with red center) overlaid on sphere
    shield = [
        ".WWW.",
        "WRRRW",
        "WRRRW",
        ".WWW.",
    ]
    c.stamp(sphere_cx - 2, sphere_cy - 2, shield, {"W": WHITE, "R": PORTUGAL_RED})
    return c


def small() -> Canvas:
    c = Canvas(13, 9, PORTUGAL_RED)
    # 2:3 split → green 5 cols (0..4), red 8 cols (5..12)
    c.rect(0, 0, 4, 8, PORTUGAL_GREEN)
    # Tiny sphere hint at split: 3x3 gold with red dot
    c.rect(3, 3, 6, 5, GOLD)
    c.set(4, 4, PORTUGAL_RED)
    c.set(5, 4, PORTUGAL_RED)
    return c
