"""Procedural pixel-perfect renderer for the geometric club / signage flags.

These flags (`flag-stripe-*`, `flag-triangle-*`, `bw triangle`) ship as
18×12 PNGs with anti-aliased edges. Up-scaling that to 27×18 produces ugly
fringe. We re-render the patterns from scratch at 27×18 with two solid
colors — pixel-perfect output, no resampling involved.

Overwrites the matching entries in `images/flags_27x18/`. The country-flag
renderer (`render_flags_27x18.py`) is unaffected.

Usage:
    python3 tools/render_procedural_flags_27x18.py
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image


REPO_ROOT = Path(__file__).resolve().parent.parent

# (output dir, width, height) — emit each procedural flag at every target size
# so signage (small flag) and scoreboard (large flag) both get pixel-perfect art.
SIZES = [
    (REPO_ROOT / "images" / "flags_27x18", 27, 18),
    (REPO_ROOT / "images" / "flags_13x9", 13, 9),
]

W, H = 27, 18  # default for rendering primitives; overwritten in main()

# Colors taken from the dominant non-AA pixels of the existing 18×12 source.
COLORS = {
    "blue":   (28, 97, 172),
    "red":    (226, 0, 26),
    "white":  (255, 255, 255),
    "black":  (17, 17, 17),
    "yellow": (240, 229, 15),
    "green":  (5, 211, 24),
}


def render_stripe(c1: str, c2: str) -> Image.Image:
    """Single-stripe pattern: 1-px border of c2 top and bottom, c1 fills the rest.
    Matches the visual of the 18×12 source where the main color sits between
    thin white edges."""
    img = Image.new("RGB", (W, H), COLORS[c1])
    px = img.load()
    for x in range(W):
        px[x, 0] = COLORS[c2]
        px[x, H - 1] = COLORS[c2]
    return img


def render_triangle(c1: str, c2: str) -> Image.Image:
    """Diagonal split from top-right to bottom-left: c1 in the top-left
    triangle, c2 in the bottom-right. Sharp 1-px boundary along x*H + y*W = W*H."""
    img = Image.new("RGB", (W, H))
    px = img.load()
    boundary = W * H
    a = COLORS[c1]
    b = COLORS[c2]
    for y in range(H):
        for x in range(W):
            px[x, y] = a if (x * H + y * W) < boundary else b
    return img


# (filename without .png) → (function, args)
SPECS: dict[str, tuple[str, tuple[str, str]]] = {
    "flag-stripe-blue-white":  ("stripe",   ("blue", "white")),
    "flag-stripe-red-white":   ("stripe",   ("red", "white")),
    "flag-triangle-black-white":  ("triangle", ("black", "white")),
    "flag-triangle-blue-white":   ("triangle", ("blue", "white")),
    "flag-triangle-green-white":  ("triangle", ("green", "white")),
    "flag-triangle-red-white":    ("triangle", ("red", "white")),
    "flag-triangle-white-black":  ("triangle", ("white", "black")),
    "flag-triangle-white-blue":   ("triangle", ("white", "blue")),
    "flag-triangle-white-red":    ("triangle", ("white", "red")),
    "flag-triangle-white-yellow": ("triangle", ("white", "yellow")),
    "flag-triangle-yellow-black": ("triangle", ("yellow", "black")),
    # `bw triangle.png` in the source bank is actually blue/white (palette
    # inspected: dominant colors are #1c61ac and #ffffff). The name is
    # misleading but we reproduce the visual.
    "bw triangle":            ("triangle", ("blue", "white")),
}


def main() -> None:
    global W, H
    total = 0
    for out_dir, w, h in SIZES:
        out_dir.mkdir(parents=True, exist_ok=True)
        W, H = w, h
        print(f"--- {w}×{h} → {out_dir.relative_to(REPO_ROOT)}/ ---")
        for name, (kind, args) in SPECS.items():
            if kind == "stripe":
                img = render_stripe(*args)
            elif kind == "triangle":
                img = render_triangle(*args)
            else:
                raise ValueError(kind)
            img.save(out_dir / f"{name}.png")
            total += 1
        print(f"  rendered {len(SPECS)} flags")
    print(f"total: {total} files")


if __name__ == "__main__":
    main()
