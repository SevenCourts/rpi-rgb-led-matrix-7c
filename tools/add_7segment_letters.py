"""Add hex-digit letter glyphs (A, b, C, d, E, F) to the 7-segment BDF fonts.

The bundled `fonts/7segment/*.bdf` files were generated from 7segment.ttf with
only digits 0-9 (filename suffix `_monospace_digits`). The TTF source has the
hex letters, so we render them at the matching pixel size and append BDF entries
in-place.

Run from the repo root:
    python3 tools/add_7segment_letters.py
"""

from __future__ import annotations

import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parent.parent
TTF = REPO_ROOT / "fonts" / "7segment" / "7segment.ttf"

# (BDF file, TTF render pixel size, dwidth per glyph)
# Sizes were found by matching PIL's `getbbox('8')` height to the existing
# digit BBX height in each BDF.
TARGETS = [
    (REPO_ROOT / "fonts" / "7segment" / "7segment_26_monospace_digits.bdf", 35, 17),
    (REPO_ROOT / "fonts" / "7segment" / "7segment_45_monospace_digits.bdf", 62, 32),
    (REPO_ROOT / "fonts" / "7segment" / "7segment_66_monospace_digits.bdf", 88, 46),
]

# Code-point → character. Only chars representable on a 7-segment display.
NEW_GLYPHS = [
    ("A", 0x41),
    ("b", 0x62),
    ("C", 0x43),
    ("d", 0x64),
    ("E", 0x45),
    ("F", 0x46),
]


def render_glyph(ttf_path: Path, pixel_size: int, ch: str):
    """Render `ch` to a 1-bit PIL image cropped to its ink bounds.
    Returns (img, bbox_in_render_space) where bbox is the crop applied."""
    font = ImageFont.truetype(str(ttf_path), pixel_size)
    bbox = font.getbbox(ch)
    if not bbox or bbox[2] <= bbox[0]:
        raise ValueError(f"glyph {ch!r} has no extent")
    # Render onto a canvas big enough that anti-aliased edges are not clipped.
    canvas_w = bbox[2] + 8
    canvas_h = bbox[3] + 8
    img = Image.new("L", (canvas_w, canvas_h), 0)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), ch, fill=255, font=font)
    # Threshold to 1-bit (0 / 255) — 7-segment is solid blocks, no AA needed.
    img = img.point(lambda v: 255 if v >= 128 else 0).convert("1")
    # Crop to actual ink bounds.
    ink_bbox = img.getbbox()
    if ink_bbox is None:
        raise ValueError(f"glyph {ch!r} rendered empty")
    cropped = img.crop(ink_bbox)
    return cropped, ink_bbox


def bitmap_hex_rows(img: Image.Image) -> list[str]:
    """1-bit PIL image → BDF hex rows (each row padded to byte multiple)."""
    w, h = img.size
    px = img.load()
    bytes_per_row = (w + 7) // 8
    rows = []
    for y in range(h):
        bits = 0
        for x in range(w):
            if px[x, y]:
                bits |= 1 << (bytes_per_row * 8 - 1 - x)
        rows.append(format(bits, f"0{bytes_per_row * 2}X"))
    return rows


def build_bdf_entry(ch: str, codepoint: int, img: Image.Image,
                    dwidth: int, ink_bbox_top: int, font_ascent: int) -> str:
    """Build a single BDF glyph entry as a string."""
    w, h = img.size
    # BBX offset_x: keep glyph horizontally centered within DWIDTH advance.
    offset_x = max(0, (dwidth - w) // 2)
    # BBX offset_y: distance from baseline to glyph bottom.
    # In PIL render-space, font_ascent ≈ position of baseline. ink_bbox[1] is
    # glyph-top y (smaller = higher). So baseline-to-bottom = font_ascent - ink_bbox_bottom.
    # We approximate with: offset_y = 0 for fonts that sit on the baseline.
    # Digits in this font use offset_y=0 too, so match that.
    offset_y = 0
    swidth = round(dwidth * 1000 / 36)  # rough scaling — matches existing digits' SWIDTH ratio
    rows = bitmap_hex_rows(img)
    parts = [
        f"STARTCHAR ${codepoint:04X}",
        f"ENCODING {codepoint}",
        f"SWIDTH {swidth} 0",
        f"DWIDTH {dwidth} 0",
        f"BBX {w} {h} {offset_x} {offset_y}",
        "BITMAP",
        *rows,
        "ENDCHAR",
    ]
    return "\n".join(parts) + "\n"


def patch_bdf(bdf_path: Path, ttf_path: Path, pixel_size: int, dwidth: int) -> None:
    """Insert new glyph entries into `bdf_path` and bump the CHARS count."""
    text = bdf_path.read_text()
    # CHARS count is at the very end before glyph definitions begin.
    m = re.search(r"^CHARS (\d+)$", text, flags=re.MULTILINE)
    if not m:
        raise RuntimeError(f"no CHARS line in {bdf_path}")
    old_count = int(m.group(1))

    # Skip glyphs we already have (idempotent).
    existing_encodings = set(int(e) for e in re.findall(r"^ENCODING (\d+)$", text, flags=re.MULTILINE))

    new_entries = []
    new_chars_added = 0
    for ch, cp in NEW_GLYPHS:
        if cp in existing_encodings:
            print(f"  {bdf_path.name}: {ch!r} (U+{cp:04X}) already present, skipping")
            continue
        img, ink_bbox = render_glyph(ttf_path, pixel_size, ch)
        font = ImageFont.truetype(str(ttf_path), pixel_size)
        # ascent — used only for sanity; we hard-code offset_y=0 to mirror the digits.
        ascent = font.getmetrics()[0]
        entry = build_bdf_entry(ch, cp, img, dwidth,
                                ink_bbox_top=ink_bbox[1], font_ascent=ascent)
        new_entries.append(entry)
        new_chars_added += 1
        print(f"  {bdf_path.name}: added {ch!r} (U+{cp:04X}) — {img.size[0]}×{img.size[1]} px")

    if not new_entries:
        return

    new_count = old_count + new_chars_added
    text = re.sub(r"^CHARS \d+$", f"CHARS {new_count}", text, count=1, flags=re.MULTILINE)

    # Insert new entries just before "ENDFONT".
    text = text.replace("ENDFONT", "".join(new_entries) + "ENDFONT")
    bdf_path.write_text(text)
    print(f"  {bdf_path.name}: CHARS {old_count} → {new_count}")


def main() -> None:
    for bdf_path, pixel_size, dwidth in TARGETS:
        print(f"--- {bdf_path.name} (TTF size={pixel_size}, DWIDTH={dwidth}) ---")
        patch_bdf(bdf_path, TTF, pixel_size, dwidth)


if __name__ == "__main__":
    main()
