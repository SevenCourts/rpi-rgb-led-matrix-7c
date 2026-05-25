"""
XL1 Layout Mockup Renderer — v2
Produces pixel-accurate 320x96 PNGs for all 5 XL1 views.
Run with the project venv: .venv/bin/python spec/xl1-layouts/mockups/render.py

Font rendering: real BDF glyphs via bdflib for all fonts that load cleanly.
spleen-6x12 and spleen-5x8 use a manual BDF parser (bdflib chokes on
non-standard bitmap rows "xxxxx" in those files).

Measured glyph advances (actual, not spec estimates):
  seg45 (FONT_XL_7SEGMENT):  32px advance, 44px bbH, bbY=0
  seg66 (FONT_XXL_7SEGMENT): 46px advance, 64px bbH, bbY=0; ':' = 12px
  seg26 (FONT_L_7SEGMENT):   17px advance, 25px bbH, bbY=0; ':' = 7px
  sp32  (FONT_XXL_SPLEEN):   32px advance, 64px bbH, bbY=-12
  sp16  (FONT_XL_SPLEEN):    16px advance, 32px bbH, bbY=-6
  sp12  (FONT_L_SPLEEN):     12px advance, 24px bbH, bbY=-5
  sp8   (FONT_M_SPLEEN):      8px advance, 16px bbH, bbY=-4
  sp6   (FONT_S_SPLEEN):      6px advance, 12px bbH, bbY=-3

  '14:30' widths: seg66=195px, seg45=140px, seg26=75px
  'WELCOME' (sp32) = 224px
  'FEDERER' (sp16) = 112px, 'NADAL' (sp16) = 80px

Output:
  spec/xl1-layouts/mockups/<view>_native.png  (320x96)
  spec/xl1-layouts/mockups/<view>_8x.png      (2560x768, nearest-neighbor 8x)
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parents[3]
FONTS_DIR = ROOT / "fonts"
FLAGS_DIR = ROOT / "images" / "flags"
LOGOS_DIR = ROOT / "images" / "logos"
OUT_DIR   = Path(__file__).parent

# ── panel dimensions ───────────────────────────────────────────────────────────
W = 320
H = 96

# ── color palette (from sevencourts/rgbmatrix.py) ─────────────────────────────
COLOR_BLACK        = (0,   0,   0)
COLOR_WHITE        = (255, 255, 255)
COLOR_GREY         = (192, 192, 192)
COLOR_GREY_DARK    = (96,  96,  96)
COLOR_YELLOW       = (255, 255, 0)
COLOR_7C_GOLD      = (255, 192, 0)
COLOR_7C_BLUE      = (111, 168, 220)
COLOR_7C_DARK_GREY = (23,  23,  23)
COLOR_7C_DARK_BLUE = (37,  56,  73)
COLOR_7C_GREEN     = (147, 196, 125)

COLOR_COURT_NAME_BG = COLOR_7C_DARK_BLUE


# ══════════════════════════════════════════════════════════════════════════════
# BDF font loader — bdflib-based with manual fallback for non-standard files
# ══════════════════════════════════════════════════════════════════════════════

class BDFGlyph:
    def __init__(self, advance, bbW, bbH, bbX, bbY, rows):
        self.advance = advance   # horizontal advance in pixels
        self.bbW     = bbW       # bounding box width
        self.bbH     = bbH       # bounding box height
        self.bbX     = bbX       # x offset: pen-x to left of bbox
        self.bbY     = bbY       # y offset: baseline to bottom of bbox (negative = below baseline)
        self.rows    = rows      # list[list[bool]], top-to-bottom, length=bbH


class BDFFont:
    def __init__(self, path):
        self.path   = path
        self.glyphs = {}         # codepoint -> BDFGlyph
        self._load()

    def _load(self):
        try:
            from bdflib import reader as bdfreader
            with open(self.path, "rb") as f:
                font = bdfreader.read_bdf(f)
            for cp, g in font.glyphs_by_codepoint.items():
                rows = [list(row_gen) for row_gen in g.iter_pixels()]
                self.glyphs[cp] = BDFGlyph(g.advance, g.bbW, g.bbH, g.bbX, g.bbY, rows)
        except Exception:
            self._load_manual()

    def _load_manual(self):
        """Pure-Python BDF parser, tolerant of non-hex bitmap rows."""
        with open(self.path, "r", encoding="latin-1") as f:
            lines = f.readlines()
        i, cur = 0, None
        while i < len(lines):
            ln = lines[i].strip()
            if ln.startswith("STARTCHAR"):
                cur = {"name": ln[10:].strip()}
            elif ln.startswith("ENCODING") and cur is not None:
                cur["codepoint"] = int(ln.split()[1])
            elif ln.startswith("DWIDTH") and cur is not None:
                cur["advance"] = int(ln.split()[1])
            elif ln.startswith("BBX") and cur is not None:
                p = ln.split()
                cur["bbW"], cur["bbH"], cur["bbX"], cur["bbY"] = int(p[1]), int(p[2]), int(p[3]), int(p[4])
            elif ln == "BITMAP" and cur is not None:
                rows, bbH, bbW = [], cur.get("bbH", 0), cur.get("bbW", 0)
                i += 1
                while i < len(lines) and lines[i].strip() != "ENDCHAR":
                    hex_row = lines[i].strip()
                    try:
                        val  = int(hex_row, 16)
                        bits = [(val >> (len(hex_row)*4 - 1 - b)) & 1 == 1 for b in range(len(hex_row)*4)]
                        rows.append((bits[:bbW] + [False]*bbW)[:bbW])
                    except ValueError:
                        pass
                    i += 1
                while len(rows) < bbH:
                    rows.append([False]*bbW)
                cur["rows"] = rows[:bbH]
                if "codepoint" in cur and cur["codepoint"] >= 0:
                    cp = cur["codepoint"]
                    self.glyphs[cp] = BDFGlyph(
                        cur.get("advance", bbW), bbW, bbH,
                        cur.get("bbX", 0), cur.get("bbY", 0), cur["rows"])
                cur = None
            i += 1

    def glyph(self, char):
        return self.glyphs.get(ord(char))


def load_fonts():
    return {
        "seg66": BDFFont(FONTS_DIR / "7segment" / "7segment_66_monospace_digits.bdf"),
        "seg45": BDFFont(FONTS_DIR / "7segment" / "7segment_45_monospace_digits.bdf"),
        "seg26": BDFFont(FONTS_DIR / "7segment" / "7segment_26_monospace_digits.bdf"),
        "sp32":  BDFFont(FONTS_DIR / "spleen-2.1.0" / "spleen-32x64.bdf"),
        "sp16":  BDFFont(FONTS_DIR / "spleen-2.1.0" / "spleen-16x32.bdf"),
        "sp12":  BDFFont(FONTS_DIR / "spleen-2.1.0" / "spleen-12x24.bdf"),
        "sp8":   BDFFont(FONTS_DIR / "spleen-2.1.0" / "spleen-8x16.bdf"),
        "sp6":   BDFFont(FONTS_DIR / "spleen-2.1.0" / "spleen-6x12.bdf"),
        "sp5":   BDFFont(FONTS_DIR / "spleen-5x8-german-characters" / "spleen-5x8.bdf"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Drawing primitives
# ══════════════════════════════════════════════════════════════════════════════

def new_canvas():
    return Image.new("RGB", (W, H), COLOR_BLACK)


def draw_glyph(img, glyph, x, y_baseline, color):
    """
    Draw one BDF glyph.
    x          = pen x (left edge of advance box)
    y_baseline = y of baseline (BDF convention)

    top_y of glyph in PIL coords = y_baseline - (bbY + bbH - 1)
      For bbY=0  (7-segment): top_y = y_baseline - (bbH - 1)
      For bbY=-n (Spleen):    top_y = y_baseline - (-n + bbH - 1) = y_baseline - bbH + 1 + n
    """
    top_y  = y_baseline - (glyph.bbY + glyph.bbH - 1)
    left_x = x + glyph.bbX
    px     = img.load()
    for row_idx, row in enumerate(glyph.rows):
        py = top_y + row_idx
        for col_idx, bit in enumerate(row):
            if bit:
                px_x = left_x + col_idx
                if 0 <= px_x < W and 0 <= py < H:
                    px[px_x, py] = color


def draw_text(img, font, text, x, y_baseline, color):
    """Draw string left-to-right, return pen x after last char."""
    pen_x = x
    for ch in text:
        g = font.glyph(ch)
        if g is None:
            pen_x += 8
            continue
        draw_glyph(img, g, pen_x, y_baseline, color)
        pen_x += g.advance
    return pen_x


def text_width(font, text):
    return sum((font.glyph(ch).advance if font.glyph(ch) else 8) for ch in text)


def _glyph_ink_left(g):
    """Leftmost lit column index within the glyph rows (0-based within bbW)."""
    for row in g.rows:
        for col, bit in enumerate(row):
            if bit:
                return col
    return 0


def _glyph_ink_right(g):
    """Rightmost lit column index within the glyph rows (0-based within bbW)."""
    best = 0
    for row in g.rows:
        for col, bit in enumerate(row):
            if bit:
                best = max(best, col)
    return best


def draw_text_ink_packed(img, font, text, x_right, y_baseline, color, inter_gap=3):
    """
    Draw a short string (1–3 chars) right-aligned so the rightmost ink pixel
    of the last character lands at x_right. Characters are packed using their
    actual ink extents with inter_gap px between adjacent ink edges.

    Returns the x of the leftmost ink pixel drawn.
    """
    chars = [ch for ch in text if font.glyph(ch) is not None]
    if not chars:
        return x_right

    glyphs = [font.glyph(ch) for ch in chars]

    # Compute ink extents for each glyph (relative to pen position)
    # abs_ink_left[i]  = pen_i + bbX + ink_col_min
    # abs_ink_right[i] = pen_i + bbX + ink_col_max

    # Work right-to-left: position last glyph so its ink right edge = x_right
    n = len(glyphs)
    pen_positions = [0] * n

    # Last glyph: ink right = pen + bbX + ink_right_col = x_right
    ink_right_last = _glyph_ink_right(glyphs[-1])
    pen_positions[-1] = x_right - (glyphs[-1].bbX + ink_right_last)

    # Each preceding glyph: its ink right edge = next glyph's ink left edge - inter_gap - 1
    for i in range(n - 2, -1, -1):
        next_ink_left_abs = pen_positions[i + 1] + glyphs[i + 1].bbX + _glyph_ink_left(glyphs[i + 1])
        # This glyph's ink right = next_ink_left_abs - inter_gap - 1
        target_ink_right_abs = next_ink_left_abs - inter_gap - 1
        ink_right_i = _glyph_ink_right(glyphs[i])
        pen_positions[i] = target_ink_right_abs - (glyphs[i].bbX + ink_right_i)

    for pen_x, g in zip(pen_positions, glyphs):
        draw_glyph(img, g, pen_x, y_baseline, color)

    leftmost_ink = pen_positions[0] + glyphs[0].bbX + _glyph_ink_left(glyphs[0])
    return leftmost_ink


def fill_rect(img, x0, y0, x1, y1, color):
    ImageDraw.Draw(img).rectangle([(x0, y0), (x1, y1)], fill=color)


def draw_diamond(img, cx, cy, r, color):
    """
    Draw a filled diamond (rotated square) centered at (cx,cy) with radius r.
    r=3 → 7px wide/tall, matching the 7×7 service ball spec.
    Pixels: all (x,y) where |x-cx| + |y-cy| <= r.
    """
    px = img.load()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if abs(dx) + abs(dy) <= r:
                xx, yy = cx + dx, cy + dy
                if 0 <= xx < W and 0 <= yy < H:
                    px[xx, yy] = color


def draw_hline(img, x0, x1, y, color):
    ImageDraw.Draw(img).line([(x0, y), (x1, y)], fill=color)


def draw_vline(img, x, y0, y1, color):
    ImageDraw.Draw(img).line([(x, y0), (x, y1)], fill=color)


def y_baseline_for_vcenter(zone_top, zone_h, font, char='0'):
    """
    Baseline y that vertically centers the glyph bounding box in the zone.
    Works for both bbY=0 (7-segment) and bbY<0 (Spleen descenders).
    """
    g = font.glyph(char)
    if g is None:
        return zone_top + zone_h // 2
    # Center the bbH-pixel box in zone_h
    top_y    = zone_top + (zone_h - g.bbH) // 2
    # baseline = top_y + (bbY + bbH - 1)
    return top_y + (g.bbY + g.bbH - 1)


def load_flag(country, tw=27, th=18):
    path = FLAGS_DIR / f"{country.lower()}.png"
    if path.exists():
        return Image.open(path).convert("RGB").resize((tw, th), Image.NEAREST)
    return Image.new("RGB", (tw, th), (80, 80, 80))


def paste_image_on_black(canvas, img_rgba, x, y):
    """Composite RGBA image onto black canvas using alpha channel."""
    if img_rgba.mode != "RGBA":
        img_rgba = img_rgba.convert("RGBA")
    # Composite over the canvas region
    region = canvas.crop((x, y, x + img_rgba.width, y + img_rgba.height))
    region_rgba = region.convert("RGBA")
    composited = Image.alpha_composite(region_rgba, img_rgba)
    canvas.paste(composited.convert("RGB"), (x, y))


def save(img, name, scale=8):
    native = OUT_DIR / f"{name}_native.png"
    scaled = OUT_DIR / f"{name}_8x.png"
    img.save(native)
    img.resize((W * scale, H * scale), Image.NEAREST).save(scaled)
    print(f"  {native.name}  +  {scaled.name}")


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 1: SCOREBOARD
#
# Geometry (decisions.md, ink-measured):
#   Panel 320×96. Team halves: y=0..46 (47px), divider y=47, y=48..94 (47px).
#   Name zone: x=0..169 (170px). Score zone: x=170..319 (150px).
#
#   Score zone breakdown (left-to-right within x=170..319):
#     Set col 1:  x=170..191  (22px)   — center sp12 digit inside
#     Set col 2:  x=192..213  (22px)
#     Set col 3:  x=214..235  (22px)   — rightmost set col ink ends ~x=230
#     Gap:        x=236..241  (6px)    — clear visual break
#     Srv diamond: center x=245, r=3   — occupies x=242..248, y_center of half
#     Gap:        x=249..252  (4px)
#     Game zone:  x=253..316  (64px)   — INK right-aligned to x=315
#     Right margin: x=316..319 (4px)
#
#   Game score rendering: draw_text_ink_packed(), right-aligns rightmost ink
#   pixel to x=315, packs multi-digit strings by ink extent (not advance),
#   inter_gap=4px. This closes the "1" orphan gap: "15" reads as a unit.
#
#   Service ball: filled diamond (r=3) → 7px wide / 7px tall, looks round at LED scale.
#   Flags: 27×18px nearest-neighbor from 18×12 source.
#   Name font: sp16 (FONT_XL_SPLEEN, 16px advance, 32px bbH, bbY=-6)
#   Set font:  sp12 (FONT_L_SPLEEN,  12px advance, 24px bbH, bbY=-5)
#   Game font: seg45 (FONT_XL_7SEGMENT, 32px advance, 44px bbH, bbY=0)
# ══════════════════════════════════════════════════════════════════════════════

def render_scoreboard(F):
    img   = new_canvas()
    seg45 = F["seg45"]
    sp12  = F["sp12"]
    sp16  = F["sp16"]

    FLAG_W, FLAG_H = 27, 18
    FLAG_MARGIN    = 3
    FLAG_GAP       = 2
    X_NAME         = FLAG_MARGIN + FLAG_W + FLAG_GAP   # x=32

    # Score zone
    X_SET          = [170, 192, 214]   # 3 set columns, 22px each
    SRV_CX         = 245               # service diamond center x
    SRV_R          = 3                 # diamond radius → 7px span
    X_GAME_INK_RIGHT = 315             # rightmost game ink pixel target

    HALF_H = 47

    # Dim fill behind game score column so the thin '1' reads as part of a slot
    # COLOR_7C_GREY = (50,50,50) — barely visible, just enough to frame the zone
    GAME_ZONE_BG = (18, 18, 18)
    fill_rect(img, 253, 0, 319, H - 1, GAME_ZONE_BG)

    teams = [
        # (zone_top, country, name, sets, game, serving)
        (0,  "germany", "FEDERER", [6, 7, 3], "15", True),
        (48, "spain",   "NADAL",   [4, 5, 6], "40", False),
    ]

    for zone_top, country, name, sets, game, serving in teams:
        # ── flag ──────────────────────────────────────────────────────────────
        flag_y = zone_top + (HALF_H - FLAG_H) // 2
        img.paste(load_flag(country, FLAG_W, FLAG_H), (FLAG_MARGIN, flag_y))

        # ── name ──────────────────────────────────────────────────────────────
        name_baseline = y_baseline_for_vcenter(zone_top, HALF_H, sp16, 'A')
        draw_text(img, sp16, name, X_NAME, name_baseline, COLOR_WHITE)

        # ── set scores — centered within each 22px column ─────────────────────
        set_baseline = y_baseline_for_vcenter(zone_top, HALF_H, sp12, '6')
        if zone_top == 0:
            set_colors = [COLOR_WHITE, COLOR_WHITE, COLOR_GREY]  # T1: won 6,7; losing 3
        else:
            set_colors = [COLOR_GREY, COLOR_GREY, COLOR_WHITE]   # T2: lost 4,5; won 6

        for i, (score, col) in enumerate(zip(sets, set_colors)):
            s  = str(score)
            sw = text_width(sp12, s)
            sx = X_SET[i] + (22 - sw) // 2
            draw_text(img, sp12, s, sx, set_baseline, col)

        # ── service diamond ───────────────────────────────────────────────────
        if serving:
            srv_cy = zone_top + HALF_H // 2
            draw_diamond(img, SRV_CX, srv_cy, SRV_R, COLOR_YELLOW)

        # ── game score — fixed-advance right-aligned to X_GAME_INK_RIGHT ───────
        # 7-segment is an inherently monospace display: every digit occupies
        # the same 32px advance slot. Right-align by total advance width so
        # "15" and "40" both have their right advance edge at the same x.
        # The thin '1' is authentic to the font style.
        game_base = y_baseline_for_vcenter(zone_top, HALF_H, seg45, '1')
        game_w    = text_width(seg45, game)
        gx        = X_GAME_INK_RIGHT - game_w + 1
        draw_text(img, seg45, game, gx, game_base, COLOR_WHITE)

    # ── divider ───────────────────────────────────────────────────────────────
    draw_hline(img, 0, W - 1, 47, COLOR_7C_DARK_GREY)

    # ── status dot — bottom-right 4×4 green ──────────────────────────────────
    fill_rect(img, 313, 91, 316, 94, COLOR_7C_GREEN)

    return img


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 2: CLOCK
# FONT_XXL_7SEGMENT "14:30" centered. seg66 '14:30' = 195px.
# Centered x = (320-195)//2 = 62. Baseline y=79 (glyph 16..78 in 96px panel).
# ══════════════════════════════════════════════════════════════════════════════

def render_clock(F):
    img    = new_canvas()
    seg66  = F["seg66"]
    time_s = "14:30"
    tw     = text_width(seg66, time_s)
    cx     = (W - tw) // 2
    base   = y_baseline_for_vcenter(0, H, seg66, '1')
    draw_text(img, seg66, time_s, cx, base, COLOR_WHITE)
    return img


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 3: IMAGE (logo + clock side-by-side)
# Left 160px: SevenCourts logo (RGBA, composited over black).
# Right 160px: "14:30" in seg45, centered.
# Vertical separator at x=159.
# ══════════════════════════════════════════════════════════════════════════════

def render_image(F):
    img   = new_canvas()
    seg45 = F["seg45"]

    # Logo zone — composite RGBA logo over black (eliminates white bg)
    logo_path = LOGOS_DIR / "Saarland Open ITF" / "saarland-open-10-v3.png"
    if not logo_path.exists():
        logo_path = LOGOS_DIR / "7C" / "sevencourts_7c_64x32.png"

    logo_rgba = Image.open(logo_path).convert("RGBA")
    lw, lh    = logo_rgba.size

    # Scale to fit 160×96 maintaining aspect ratio
    scale = min(160 / lw, 96 / lh)
    nw, nh = int(lw * scale), int(lh * scale)
    logo_scaled = logo_rgba.resize((nw, nh), Image.NEAREST)

    lx = (160 - nw) // 2
    ly = (96  - nh) // 2
    paste_image_on_black(img, logo_scaled, lx, ly)

    # Clock zone — centered in x=160..319
    time_s = "14:30"
    tw     = text_width(seg45, time_s)
    cx     = 160 + (160 - tw) // 2
    base   = y_baseline_for_vcenter(0, H, seg45, '1')
    draw_text(img, seg45, time_s, cx, base, COLOR_WHITE)

    # Vertical separator
    draw_vline(img, 159, 0, H - 1, COLOR_7C_DARK_GREY)

    return img


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 4: MESSAGE
# "WELCOME" in sp32 (FONT_XXL_SPLEEN), COLOR_7C_BLUE, centered in y=0..68.
# Divider at y=69 (COLOR_7C_DARK_GREY).
# Clock "14:30" in seg26 (FONT_L_7SEGMENT), right-aligned, COLOR_GREY_DARK,
# vertically centered in clock strip y=70..95.
# ══════════════════════════════════════════════════════════════════════════════

def render_message(F):
    img   = new_canvas()
    sp32  = F["sp32"]
    seg26 = F["seg26"]

    # Message — centered in message zone y=0..68 (69px)
    msg      = "WELCOME"
    mw       = text_width(sp32, msg)
    mx       = (W - mw) // 2
    msg_base = y_baseline_for_vcenter(0, 69, sp32, 'W')
    draw_text(img, sp32, msg, mx, msg_base, COLOR_7C_BLUE)

    # Divider
    draw_hline(img, 0, W - 1, 69, COLOR_7C_DARK_GREY)

    # Clock strip y=70..95 (26px)
    time_s     = "14:30"
    tw         = text_width(seg26, time_s)
    cx         = W - tw - 4       # right-aligned, 4px margin
    clock_base = y_baseline_for_vcenter(70, 26, seg26, '1')
    draw_text(img, seg26, time_s, cx, clock_base, COLOR_GREY_DARK)

    return img


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 5: SIGNAGE — 2×2 grid, 4 courts
#
# Cell size: 160×48px.
# Within each cell (absolute coords for top-left cell, offsets applied for others):
#   y=0..11  Court name strip (12px, COLOR_COURT_NAME_BG fill)
#   y=12     1px separator (COLOR_7C_DARK_GREY)
#   y=13..29 Team 1 row (17px)
#   y=30..46 Team 2 row (17px)
#   y=47     1px bottom cell border
#
# Score zone (within-cell x, cell width=160):
#   Flags: 18×12px (standard), at cell_x+2, vertically centered in 17px row
#   Name: sp6 (FONT_S_SPLEEN), starts at cell_x+22
#   Score zone right portion — within-cell x:
#     X_SET[0,1,2] = 106, 113, 120  (sets, 6px advance each, 7px columns)
#     X_SRV        = 128            (4×4 service dot)
#     X_GAME_RIGHT = 158            (game score right edge, sp8 8px advance)
#   Total score zone = 158-106 = 52px
#   Name zone = 106 - 22 = 84px → 14 chars at sp6
# ══════════════════════════════════════════════════════════════════════════════

def render_signage(F):
    img = new_canvas()
    sp6 = F["sp6"]
    sp8 = F["sp8"]

    FLAG_W, FLAG_H = 18, 12
    CELL_W, CELL_H = 160, 48
    HDR_H          = 12
    ROW_H          = 17        # (48 - 12 - 1) // 2 = 17
    # Within-cell score layout (all coords relative to cell left edge)
    #
    # Score zone breakdown (right side of 160px cell):
    #   sp6 glyph: advance=6, ink right=col4 → effective ink width=5px, right dead=1px
    #   Set cols: 3 × 10px pitch → gap between ink edges = 10-5 = 5px ✓ clearly separated
    #     x=92, 102, 112 → last digit ink x=112..116
    #   Gap:      x=117..120 (4px)
    #   Srv dot:  4×4 → x=121..124
    #   Gap:      x=125..128 (4px)
    #   Game:     sp8 right-aligned to x=157, "AD"=16px → x=142..157
    #   Right margin: x=158..159 (2px)
    # Name zone: x=20..91 = 72px → ~12 chars at sp6 (sufficient for most names)
    X_SET_COLS   = [92, 102, 112]    # 3 set digit columns, 10px pitch
    X_SRV_DOT    = 121               # service dot left edge (4×4 px)
    X_GAME_RIGHT = 158               # game score right edge (exclusive)

    courts = [
        # (row, col, court_name, c1, n1, sets1, c2, n2, sets2, game1, game2, t1_serving)
        (0, 0, "COURT 1", "germany", "FEDERER",   [6,7],    "spain",   "NADAL",     [4,5],    "15", "40", True),
        (0, 1, "COURT 2", "serbia",  "DJOKOVIC",  [3,6],    "spain",   "ALCARAZ",   [6,4],    "40", "AD", False),
        (1, 0, "COURT 3", "germany", "ZVEREV",    [6],      "norway",  "RUUD",      [4],      "15", "0",  True),
        (1, 1, "COURT 4", "russia",  "MEDVEDEV",  [3,6,5],  "greece",  "TSITSIPAS", [6,4,3],  "0",  "30", False),
    ]

    for (crow, ccol, court_name, c1, n1, s1, c2, n2, s2, g1, g2, t1_srv) in courts:
        ox = ccol * CELL_W   # cell origin x
        oy = crow * CELL_H   # cell origin y

        # ── court name header strip ───────────────────────────────────────────
        fill_rect(img, ox, oy, ox + CELL_W - 2, oy + HDR_H - 1, COLOR_COURT_NAME_BG)
        draw_text(img, sp6, court_name, ox + 2, oy + 10, COLOR_GREY)

        # ── separator below header ────────────────────────────────────────────
        draw_hline(img, ox, ox + CELL_W - 2, oy + HDR_H, COLOR_7C_DARK_GREY)

        # ── team rows ─────────────────────────────────────────────────────────
        team_data = [
            (c1, n1, s1, g1, t1_srv),
            (c2, n2, s2, g2, not t1_srv),
        ]
        for t_idx, (country, name, sets, game, serving) in enumerate(team_data):
            row_top = oy + HDR_H + 1 + t_idx * ROW_H   # y=oy+13 or oy+30

            # Flag (18×12) vertically centered in 17px row
            flag     = load_flag(country, FLAG_W, FLAG_H)
            flag_y   = row_top + (ROW_H - FLAG_H) // 2
            img.paste(flag, (ox + 2, flag_y))

            # Name — sp6 glyph 12px, center in 17px row
            name_base = row_top + (ROW_H - sp6.glyph('A').bbH) // 2 + (sp6.glyph('A').bbY + sp6.glyph('A').bbH - 1)
            draw_text(img, sp6, name[:14], ox + FLAG_W + 4, name_base, COLOR_GREY)

            # Set scores — right-pack into the 3 set columns
            # Opponent sets for won/lost coloring
            opp_sets = s2 if t_idx == 0 else s1
            n_sets   = len(sets)
            start_col = 3 - n_sets   # right-align: 1 set→col2, 2 sets→col1+2, 3→all
            for i, score in enumerate(sets):
                col_idx = start_col + i
                sx      = ox + X_SET_COLS[col_idx]
                won     = (i < len(opp_sets) and score > opp_sets[i])
                set_col = COLOR_WHITE if won else COLOR_GREY
                draw_text(img, sp6, str(score), sx, name_base, set_col)

            # Service dot (4×4 yellow)
            if serving:
                sdot_y = row_top + (ROW_H - 4) // 2
                fill_rect(img, ox + X_SRV_DOT, sdot_y,
                          ox + X_SRV_DOT + 3, sdot_y + 3, COLOR_YELLOW)

            # Game score — sp8, right-aligned to X_GAME_RIGHT
            game_w    = text_width(sp8, game)
            game_x    = ox + X_GAME_RIGHT - game_w
            game_base = row_top + (ROW_H - sp8.glyph('0').bbH) // 2 + (sp8.glyph('0').bbY + sp8.glyph('0').bbH - 1)
            draw_text(img, sp8, game, game_x, game_base, COLOR_WHITE)

        # ── bottom cell border ────────────────────────────────────────────────
        draw_hline(img, ox, ox + CELL_W - 1, oy + CELL_H - 1, COLOR_7C_DARK_GREY)

    # ── grid dividers ─────────────────────────────────────────────────────────
    draw_vline(img, CELL_W - 1, 0, H - 1, COLOR_7C_DARK_GREY)    # vertical center
    draw_hline(img, 0, W - 1, CELL_H,     COLOR_7C_DARK_GREY)    # horizontal center

    return img


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Loading fonts…")
    F = load_fonts()
    print(f"  Loaded: {', '.join(F)}")

    views = [
        ("scoreboard", render_scoreboard),
        ("clock",      render_clock),
        ("image",      render_image),
        ("message",    render_message),
        ("signage",    render_signage),
    ]

    print(f"\nRendering → {OUT_DIR}/")
    for name, fn in views:
        print(f"\n[{name}]")
        save(fn(F), name)

    print("\nDone.")
