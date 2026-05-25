"""Contact sheet for hand-authored flags.

Renders each flag at 10x scale beside a freshly-computed Lanczos version
(from the HiDPI webp source, or the 18x12 fallback) for comparison.

Output: spec/xl1-layouts/mockups/flags_handdrawn_large.png
        spec/xl1-layouts/mockups/flags_handdrawn_small.png
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from flag_pixels import FLAGS  # noqa: E402


SCALE = 10
LARGE_W, LARGE_H = 27, 18
SMALL_W, SMALL_H = 13, 9

LABEL_H = 18
GUTTER = 26
ROW_PAD = 14

SRC_BIG = REPO_ROOT / "images" / "flags" / "big"
SRC_18x12 = REPO_ROOT / "images" / "flags"
OUT_DIR = REPO_ROOT / "spec" / "xl1-layouts" / "mockups"


def _font(size: int = 13):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/TTF/DejaVuSans.ttf"):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _upscale(img: Image.Image, scale: int) -> Image.Image:
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)


def _lanczos_reference(name: str, w: int, h: int) -> Image.Image | None:
    """Compute what the Lanczos pipeline would produce — quantized to 16 colors
    to match the production pipeline for these specific flags."""
    big = SRC_BIG / f"{name}.webp"
    small = SRC_18x12 / f"{name}.png"
    if big.exists():
        src = Image.open(big).convert("RGB")
    elif small.exists():
        src = Image.open(small).convert("RGB")
    else:
        return None
    resized = src.resize((w, h), Image.LANCZOS)
    pal = resized.quantize(colors=16, method=Image.Quantize.MEDIANCUT)
    return pal.convert("RGB")


def render_sheet(size_label: str, w: int, h: int, get_canvas, out: Path) -> None:
    font = _font(13)
    title_font = _font(16)
    names = list(FLAGS.keys())

    cell_img_w = w * SCALE
    cell_img_h = h * SCALE
    pair_w = cell_img_w * 2 + 16
    cell_h = LABEL_H + cell_img_h + ROW_PAD

    cols = 2
    rows = (len(names) + cols - 1) // cols

    margin = 16
    sheet_w = margin * 2 + cols * pair_w + (cols - 1) * GUTTER
    sheet_h = margin * 2 + LABEL_H + 8 + rows * cell_h

    img = Image.new("RGB", (sheet_w, sheet_h), (28, 28, 32))
    draw = ImageDraw.Draw(img)
    draw.text((margin, 6),
              f"Hand-drawn (left) vs Lanczos+quantize (right) — {size_label}",
              fill=(230, 230, 230), font=title_font)

    for i, name in enumerate(names):
        col = i % cols
        row = i // cols
        cx = margin + col * (pair_w + GUTTER)
        cy = margin + LABEL_H + 8 + row * cell_h

        draw.text((cx, cy), name, fill=(230, 230, 230), font=font)

        # Hand-drawn
        hand = get_canvas(name).to_pil()
        img.paste(_upscale(hand, SCALE), (cx, cy + LABEL_H))

        # Lanczos reference
        ref = _lanczos_reference(name, w, h)
        if ref is not None:
            img.paste(_upscale(ref, SCALE), (cx + cell_img_w + 16, cy + LABEL_H))
        else:
            draw.text((cx + cell_img_w + 16, cy + LABEL_H + cell_img_h // 2 - 8),
                      "(no source)", fill=(160, 160, 160), font=font)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"wrote {out}")


def main() -> None:
    render_sheet("27x18 (scoreboard)", LARGE_W, LARGE_H,
                 lambda n: FLAGS[n].large(),
                 OUT_DIR / "flags_handdrawn_large.png")
    render_sheet("13x9 (signage)", SMALL_W, SMALL_H,
                 lambda n: FLAGS[n].small(),
                 OUT_DIR / "flags_handdrawn_small.png")


if __name__ == "__main__":
    main()
