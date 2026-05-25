"""Render hand-authored pixel-perfect flags to images/flags_27x18 and _13x9.

Each module under tools/flag_pixels/ exports `large()` -> 27x18 Canvas and
`small()` -> 13x9 Canvas. The Lanczos pipeline that produced the current mushy
PNGs (render_flags_27x18.py) writes the full library; this tool overwrites
just the entries it knows about.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from flag_pixels import FLAGS  # noqa: E402


OUT_27 = REPO_ROOT / "images" / "flags_27x18"
OUT_13 = REPO_ROOT / "images" / "flags_13x9"


def main() -> None:
    OUT_27.mkdir(parents=True, exist_ok=True)
    OUT_13.mkdir(parents=True, exist_ok=True)

    for name, mod in FLAGS.items():
        large = mod.large()
        small = mod.small()
        assert large.w == 27 and large.h == 18, (name, large.w, large.h)
        assert small.w == 13 and small.h == 9, (name, small.w, small.h)
        large.to_pil().save(OUT_27 / f"{name}.png")
        small.to_pil().save(OUT_13 / f"{name}.png")
        print(f"wrote {name}.png  (27x18 + 13x9)")


if __name__ == "__main__":
    main()
