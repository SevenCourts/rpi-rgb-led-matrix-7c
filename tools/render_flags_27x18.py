"""Render the country-flag bank at 27×18 / 13×9 px for L1 / XL1 panels.

KNOWN ISSUE — some Lanczos-downsampled flags still look mushy at 27×18
(diagonal lines, fine emblems). Examples flagged on the bench:
  - Union Jack family (Australia, New Zealand, Great Britain, Fiji, Tuvalu) —
    diagonal crosses don't quantize cleanly even at palette=16.
  - Complex emblems (Mexico, Sri Lanka, Brazil) — center motif loses shape.
  - Some three-stripe + emblem flags (Spain, Portugal) — emblem fuzz.

NEXT STEP for these: hand-redraw at 27×18 (and 13×9) in a pixel editor. The
loader (`sevencourts.images.load_flag_image`) returns the native-size PNG
verbatim when present, so any hand-tuned art drops in without code changes.
PALETTE_SIZE_OVERRIDES below is the hand-tunable knob for an intermediate
quick fix per flag.

Output: `images/flags_27x18/<name>.png` and `images/flags_13x9/<name>.png`.

Source priority:
1. High-resolution `.webp` in `images/flags/big/` (1000-px wide) — preferred,
   gives Lanczos a clean source to downsample from.
2. Existing `images/flags/*.png` at 18×12 — fallback for flags we don't have
   a HiDPI source for.

Pipeline:
1. Load source.
2. Downsample to target with Lanczos.
3. Color-quantize with median cut to kill the anti-aliased fringe; palette
   size is per-flag tunable in PALETTE_SIZE_OVERRIDES (default 6).
4. Save PNG.

Usage:
    python3 tools/render_flags_27x18.py
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image


REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_BIG = REPO_ROOT / "images" / "flags" / "big"
SRC_SMALL = REPO_ROOT / "images" / "flags"

# (output dir, width, height) — same generator runs for every panel-native size.
TARGETS = [
    (REPO_ROOT / "images" / "flags_27x18", 27, 18),
    (REPO_ROOT / "images" / "flags_13x9", 13, 9),
]

# Flags with sharp diagonals or fine emblems need a larger palette so the
# Lanczos-induced fringe survives quantization without collapsing into mush.
PALETTE_SIZE_OVERRIDES = {
    # Union Jack family — diagonal crosses
    "great britain": 16,
    "australia": 16,
    "new zealand": 16,
    "fiji": 16,
    "tuvalu": 16,
    # Multi-color emblems
    "united states of america": 12,
    "usa": 12,
    "brazil": 12,
    "mexico": 16,
    "sri lanka": 16,
    "argentina": 12,
    # Three-stripe + center emblem
    "egypt": 12,
    "iran": 12,
    "saudi arabia": 12,
    "kazakhstan": 12,
    "turkmenistan": 16,
    "spain": 12,
    "portugal": 12,
    "ecuador": 12,
    "guatemala": 12,
    "albania": 12,
    "andorra": 12,
}
DEFAULT_PALETTE_SIZE = 6


def quantize(img: Image.Image, n_colors: int) -> Image.Image:
    """Median-cut quantize to at most `n_colors`. Returns an RGB image."""
    pal = img.convert("RGB").quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT)
    return pal.convert("RGB")


# Procedural-rendered flags (stripes / triangles) are produced by
# `render_procedural_flags_27x18.py`; this generator must not overwrite them
# with the upscale fallback.
PROCEDURAL_FLAGS = frozenset({
    "flag-stripe-blue-white", "flag-stripe-red-white",
    "flag-triangle-black-white", "flag-triangle-blue-white",
    "flag-triangle-green-white", "flag-triangle-red-white",
    "flag-triangle-white-black", "flag-triangle-white-blue",
    "flag-triangle-white-red", "flag-triangle-white-yellow",
    "flag-triangle-yellow-black", "bw triangle",
})


def render_one(name: str, out_dir: Path, target: tuple[int, int]) -> tuple[str, str]:
    """Render `images/flags/<name>.png` at the given target size."""
    if name in PROCEDURAL_FLAGS:
        return (name, "procedural-skipped")
    big = SRC_BIG / f"{name}.webp"
    small = SRC_SMALL / f"{name}.png"
    if big.exists():
        src = Image.open(big).convert("RGB")
        source_tag = "big"
    elif small.exists():
        src = Image.open(small).convert("RGB")
        source_tag = "small"
    else:
        return (name, "MISSING")

    resized = src.resize(target, Image.LANCZOS)
    n_colors = PALETTE_SIZE_OVERRIDES.get(name, DEFAULT_PALETTE_SIZE)
    out = quantize(resized, n_colors)
    out.save(out_dir / f"{name}.png")
    return (name, source_tag)


def main() -> None:
    names = sorted(p.stem for p in SRC_SMALL.glob("*.png"))
    for out_dir, w, h in TARGETS:
        out_dir.mkdir(parents=True, exist_ok=True)
        counts = {"big": 0, "small": 0, "MISSING": 0, "procedural-skipped": 0}
        for name in names:
            _, tag = render_one(name, out_dir, (w, h))
            counts[tag] += 1
        print(f"--- {w}×{h} → {out_dir.relative_to(REPO_ROOT)}/ ---")
        print(f"  {counts['big']} HiDPI + {counts['small']} (18×12 upscale)"
              f" + {counts['procedural-skipped']} procedural-skipped"
              f" = {sum(counts.values()) - counts['MISSING']};"
              f" missing: {counts['MISSING']}")


if __name__ == "__main__":
    main()
