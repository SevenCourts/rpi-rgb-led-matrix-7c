"""Contact-sheet PNGs of `images/flags_27x18/` for visual review.

Flags are placed at their native 27×18 resolution (no scaling). Each cell has
a 1-px black separator from its neighbors and a small text label below the
flag. Output is split across several PNGs (~40 flags each) so individual
sheets stay viewable.

Output: `spec/xl1-layouts/mockups/flags_contact_sheet_<n>.png`.

Usage:
    python3 tools/flags_contact_sheet.py
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parent.parent
FLAGS_DIR = REPO_ROOT / "images" / "flags_27x18"
OUT_DIR = REPO_ROOT / "spec" / "xl1-layouts" / "mockups"

FLAG_W, FLAG_H = 27, 18
LABEL_H = 10
CELL_W = 64           # wide enough for ~12-char labels at the default font
CELL_H = FLAG_H + 2 + LABEL_H
COLS = 6
ROWS = 8              # 48 flags per sheet -> 4 sheets for 156 flags

BG = (32, 32, 32)
BORDER = (0, 0, 0)
TEXT = (220, 220, 220)


def _draw_cell(canvas: Image.Image, x: int, y: int, flag_path: Path,
               font: ImageFont.ImageFont) -> None:
    flag = Image.open(flag_path).convert("RGB")
    # Pad horizontally to center the 27-px flag in the wider cell.
    fx = x + (CELL_W - FLAG_W) // 2
    canvas.paste(flag, (fx, y))
    draw = ImageDraw.Draw(canvas)
    label = flag_path.stem
    if len(label) > 14:
        label = label[:13] + "…"
    bbox = draw.textbbox((0, 0), label, font=font)
    lw = bbox[2] - bbox[0]
    lx = x + (CELL_W - lw) // 2
    draw.text((lx, y + FLAG_H + 2), label, fill=TEXT, font=font)


def render_sheets() -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Wipe previous sheets so we don't keep stale extras.
    for old in OUT_DIR.glob("flags_contact_sheet_*.png"):
        old.unlink()

    flags = sorted(FLAGS_DIR.glob("*.png"))
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
    except OSError:
        font = ImageFont.load_default()

    per_sheet = COLS * ROWS
    sheet_w = COLS * CELL_W + (COLS + 1)
    sheet_h = ROWS * CELL_H + (ROWS + 1)

    produced: list[Path] = []
    for sheet_idx, start in enumerate(range(0, len(flags), per_sheet)):
        chunk = flags[start:start + per_sheet]
        img = Image.new("RGB", (sheet_w, sheet_h), BG)
        # Grid lines (1-px black borders).
        draw = ImageDraw.Draw(img)
        for c in range(COLS + 1):
            x = c * (CELL_W + 1)
            draw.line([(x, 0), (x, sheet_h - 1)], fill=BORDER)
        for r in range(ROWS + 1):
            y = r * (CELL_H + 1)
            draw.line([(0, y), (sheet_w - 1, y)], fill=BORDER)

        for i, flag_path in enumerate(chunk):
            col = i % COLS
            row = i // COLS
            x = 1 + col * (CELL_W + 1)
            y = 1 + row * (CELL_H + 1)
            _draw_cell(img, x, y, flag_path, font)

        out = OUT_DIR / f"flags_contact_sheet_{sheet_idx + 1}.png"
        img.save(out)
        produced.append(out)

    return produced


def main() -> None:
    out = render_sheets()
    for p in out:
        print(f"  {p.relative_to(REPO_ROOT)}")
    print(f"total: {len(out)} sheet(s)")


if __name__ == "__main__":
    main()
