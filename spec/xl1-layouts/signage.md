# XL1 Signage Layout

ITF tournament signage: displays up to 4 courts simultaneously in a 2×2 grid. Each cell shows team names, set scores, game score, and service indicator.

**Viewing mode:** Public, 7m+ (overview mode). Admin/close-range for reading individual scores.  
**M1 reference:** `sevencourts/m1/view_signage.py`

---

## M1 Baseline (for reference)

On M1 (192×64):
- 2×2 grid: each cell = 96×32px (`W_MATCH = 96`, `H_MATCH = 32`).
- Court name strip (top of each cell): height = `h_font_court_name + 2` = 6+2 = 8px. Background fill with `COLOR_COURT_NAME_BG` (club blue).
- Team name font: `FONT_XS_SPLEEN` (spleen-5x8, 6px glyph, 5px wide). Singles: max 14 chars. Doubles: max 3 chars per name (side by side with flag).
- Score font: `FONT_S_SPLEEN` (spleen-6x12, 8px glyph, 6px wide).
- Flag images: small variant (9×6px via `W_FLAG_SMALL × H_FLAG_SMALL`).
- Service indicator: 4×4px pixel-art dot.
- Each cell's available name zone: ~76px wide, 24px tall (32px minus 8px header).
- The `MAX_LENGTH_NAME_SINGLES = 14` and `MAX_LENGTH_NAME_DOUBLES = 3` constants reflect these tight constraints.

---

## Section 1: v1 — Same Elements, Bigger Canvas

### Design Principle

XL1 (320×96) gives each 2×2 grid cell **160×48px** (vs M1's 96×32px) — **2.5× more area per cell**. This allows:
1. Upgrade team name font from FONT_XS (6px glyph) to FONT_S (8px glyph) or FONT_M (10px glyph).
2. Upgrade score font from FONT_S (8px) to FONT_M (10px).
3. Expand name truncation limits: singles to 18–20 chars, doubles to 5–6 chars.
4. Use standard-size flags (18×12px) instead of the small variant (9×6px).

### Cell Dimensions

```
W_MATCH_XL1 = 160   (320 // 2)
H_MATCH_XL1 = 48    (96 // 2)
```

### Zone Map (one cell, showing absolute coords for top-left cell)

```
x=0                   x=159
y=0  ┌────────────────────────────┐
     │ COURT NAME   [TIME/STATUS] │  ← court name strip, y=0..11 (12px)
y=12 ├────────────────────────────┤  ← 1px separator
y=13 │ [FLAG] PLAYER 1    6  7  3 │  ← team 1 row, y=13..29 (17px)
y=30 │ [FLAG] PLAYER 2    4  5  6 │  ← team 2 row, y=30..46 (17px)
y=47 └────────────────────────────┘  ← 1px bottom separator
```

For the second row of cells (courts 3–4), all y values shift by +48.

### Court Name Strip (y=0..11, h=12px)

- Background: `COLOR_COURT_NAME_BG` (club blue, from club_styles). Width = 159px (leave 1px for cell border).
- Court name text: `FONT_XS_SPLEEN` (5px wide, 6px glyph). At 160px, fits ~30 chars. Court names are short (e.g. "Court 1", "Platz 3").
  - x=2, y=9 (baseline = h_font_court_name + 1 + strip_top = 6+1+0 = 7, add 2px padding → y=9).
  - Color: `COLOR_GREY`.
- Match status (right-aligned): same font, `COLOR_7C_GOLD`. x = 160 - width_in_pixels(font, status) - 2.

Actually, since the strip is now 12px tall (vs M1's 8px), we can upgrade to `FONT_S_SPLEEN` (6px glyph):
- h_font_court_name = 8px (FONT_S_SPLEEN glyph body). Strip height = 8 + 2 = 10px — fits in 12px.
- x=2, y=10 (baseline). Color: `COLOR_GREY`. Court name font upgrade from FONT_XS → FONT_S on XL1.

### Team Row Layout (each row: 17px, y=13..29 and y=30..46)

Each team row has:
1. Flag: 9×6px (small). OR upgrade to 18×12px (standard) — but 17px row height barely fits 12px flag. Use standard flags: y_flag = row_y + (17-12)//2 = row_y + 2.
2. Name text: follows flag at x = flag_width + 2.
3. Score: right-aligned in cell.

**Flag size decision**: Standard flags (18×12) placed at y+2 within the 17px row. Flag top = row_y+2, flag bottom = row_y+13. Leaves 4px of headroom. Acceptable.

**Name font**: `FONT_S_SPLEEN` (spleen-6x12, 8px glyph body, 6px wide).
- Available name width: 160 - 18 - 2 (flag+gap) - score_zone_width - 2 = depends on score zone.

**Score zone (right side of cell)**: 
- Using `FONT_M_SPLEEN` (spleen-8x16, 10px glyph, 8px wide) for set and game scores.  
  Wait — glyph body = 10px, row height = 17px. 10px glyph fits with 7px margin. Good.
- Game score column: "Ad" = 2 chars × 8px = 16px, plus service indicator 4px, plus gap 2px = ~22px. Allow 24px.
- Set score columns: each set digit = 1 char × 8px = 8px + 2px gap = 10px. Three sets = 30px.
- Service indicator: 4×4px. Allow 6px column.
- Total score zone = 6 (srv) + 30 (sets) + 24 (game) = 60px. x_score_zone_start = 160 - 60 = **100**.

**Name available width**: 100 - 20 (flag) - 2 = **78px** at 6px/char = **13 chars**.

This is actually the same as M1's `MAX_LENGTH_NAME_SINGLES = 14`. But on XL1, each cell is 160px wide (not 96px) — we should be able to fit more. Let's recalculate with a smaller score zone:

Revised approach: Use `FONT_S_SPLEEN` for set scores (6px wide) instead of FONT_M_SPLEEN:
- Set columns: 3 × (6+2) = 24px.
- Game score: `FONT_M_SPLEEN` (8px wide): "Ad" = 16px + 2px gap = 18px.
- Service indicator: 6px.
- Total score zone = 6 + 24 + 18 = **48px**. x_score_zone_start = 160 - 48 = **112**.
- Name width = 112 - 20 - 2 = **90px** / 6px = **15 chars**.

To get a meaningful improvement, use `FONT_M_SPLEEN` (8px wide) for names with score zone at 48px:
- Name width = 90px / 8px = **11 chars** in FONT_M (10px glyph).

Best compromise for XL1:
- Name font: `FONT_S_SPLEEN` (6px wide, 8px glyph). Name truncation: 15 chars.
- Set score font: `FONT_S_SPLEEN` (6px wide).
- Game score font: `FONT_M_SPLEEN` (8px wide).
- Service indicator: 4×4px at x_score_zone_start - 6.

`MAX_LENGTH_NAME_SINGLES` for XL1: **15** (vs M1's 14 — modest improvement).  
`MAX_LENGTH_NAME_DOUBLES`: **5** chars per player (vs M1's 3), since we have more horizontal space.

### ASCII Mockup — 2×2 grid (1 char = 8px, 40×12 grid)

```
+--------------------+--------------------+  y=0
|COURT 1      14:00  |COURT 2      14:30  |  y=0..11  (court name strip)
+--------------------+--------------------+  y=12
|[F] FEDERER  6 7 15 |[F] DJOKOVIC 3 6 40 |  y=13..29 (team1)
|[F] NADAL    4 5 30 |[F] ALCARAZ  6 4 30 |  y=30..46 (team2)
+--------------------+--------------------+  y=47..48 (between-row separator)
|COURT 3      Walko. |COURT 4      15:45  |  y=48..59 (court name strip)
+--------------------+--------------------+  y=60
|[F] ZVEREV   6 7 A  |[F] MEDVEDEV 3 6 40 |  y=61..77 (team1)
|[F] RUUD     4 5 30 |[F] TSITSIPAS6 4 0  |  y=78..94 (team2)
+--------------------+--------------------+  y=95
```

_Grid lines represent 1px separators in COLOR_7C_DARK_GREY._

### Detailed Element Coordinates (top-left cell, court 0)

| Element | x | y (baseline) | Font / Size | Color |
|---------|---|-------------|-------------|-------|
| Court name BG | 0 | 0 | fill 159×12 | COLOR_COURT_NAME_BG |
| Court name text | 2 | 10 | FONT_S_SPLEEN (6×12) | COLOR_GREY |
| Match status text | right-aligned | 10 | FONT_S_SPLEEN | COLOR_7C_GOLD |
| T1 flag | 2 | 15 (top, not baseline) | 18×12 image | — |
| T1 name | 22 | 28 | FONT_S_SPLEEN (6×12) | COLOR_GREY |
| T1 set1 | 112 | 28 | FONT_S_SPLEEN | won/lost color |
| T1 set2 | 120 | 28 | FONT_S_SPLEEN | won/lost color |
| T1 set3 | 128 | 28 | FONT_S_SPLEEN | won/lost color |
| T1 service dot | 135 | 15 | 4×4 pixel art | COLOR_GREY |
| T1 game score | 141 | 28 | FONT_M_SPLEEN (8×16) | COLOR_WHITE |
| T2 flag | 2 | 32 (top) | 18×12 image | — |
| T2 name | 22 | 45 | FONT_S_SPLEEN | COLOR_GREY |
| T2 set scores | 112..136 | 45 | FONT_S_SPLEEN | won/lost color |
| T2 game score | 141 | 45 | FONT_M_SPLEEN | COLOR_WHITE |
| H-center divider | 0 | 47 | 1px line | COLOR_7C_DARK_GREY |
| V-center divider | 159 | 0..95 | 1px line | COLOR_7C_DARK_GREY |

For courts 1, 2, 3: x offsets +0/+160/+0/+160 respectively, y offsets +0/+0/+48/+48.

### Pixel Budget Validation

- Vertical per cell: 12 (header) + 1 (sep) + 17 (T1) + 17 (T2) + 1 (bot sep) = **48px**. Fits exactly in H_MATCH_XL1 = 48.
- Horizontal score zone: 6 (srv) + 3×8 (sets) + 8×2 (game "Ad") = 6+24+16 = **46px**. Remaining = 159-46 = 113px. Flag 18px + gap 2px = 20px. Name zone = 113-20 = **93px** / 6px = 15 chars. Confirmed.
- Name baseline: y=13 (row_top) + 8px (FONT_S glyph) + 7px centering = ~28px. OK within 17px row if glyph is 8px: baseline = row_top + (17-8)//2 + 8 = row_top + 12 → y=25 for T1. (Re-adjusted in table above.)

### Constants Summary (XL1 vs M1)

| Constant | M1 | XL1 |
|----------|----|-----|
| W_MATCH | 96 | 160 |
| H_MATCH | 32 | 48 |
| FONT_SIGNAGE_COURT_NAME | FONT_XS_SPLEEN (5×8) | FONT_S_SPLEEN (6×12) |
| FONT_SIGNAGE_TEAM_NAME | FONT_XS_SPLEEN (5×8) | FONT_S_SPLEEN (6×12) |
| FONT_SIGNAGE_SCORE | FONT_S_SPLEEN (6×12) | FONT_M_SPLEEN (8×16) for game; FONT_S for sets |
| MAX_LENGTH_NAME_SINGLES | 14 | 15 |
| MAX_LENGTH_NAME_DOUBLES | 3 | 5 |
| Flag size | small (9×6) | standard (18×12) |

### Rationale

- The 2×2 grid structure is unchanged — it maps cleanly to XL1's 320×96 with cells of 160×48px.
- Font upgrades (XS→S for names, S→M for game scores) are the primary readability improvement. Game scores in FONT_M (10px glyph, 8px wide) are ~33% larger than M1's FONT_S (8px glyph, 6px wide) — noticeable at distance.
- Standard-size flags (18×12) replace small flags (9×6). This makes country identification easier and is a meaningful improvement for tournament display.
- The 1px vertical and horizontal grid lines are preserved, providing visual separation between cells without wasting significant pixels.
- Name truncation limit increases from 14 to 15 chars — modest but meaningful for players like "Djokovic" (8) vs "Schiwartzman" (12). Most names still fit without truncation.

### Constraints

- **4-court maximum**: Same as M1. The 2×2 grid structure doesn't extend to 6 courts without a layout redesign.
- **Doubles layout**: On M1, doubles abbreviates names to 3 chars side-by-side. On XL1 with 5-char limit and wider cells, two players can be displayed in a single row with: `[FLAG] PLY1  [FLAG] PLY2  scores`. This needs careful x-coordinate calculation (see v2 proposals for a richer approach).
- **Score overflow**: Scores like "7-6 (12)" (tie-break with long points) would overflow the score zone. Same limitation as M1 — no change in v1.

---

## Section 2: v2 Proposals

### Proposal A: 6-Court Grid (3×2 Layout)

**Concept:** Use XL1's extra width (128px vs M1) to fit 3 courts per row instead of 2, displaying 6 courts simultaneously. Each cell: 106×48px.

```
+-------------+-------------+-------------+  y=0
|COURT 1 14:00|COURT 2 14:30|COURT 3 15:00|  (court name strip)
+-------------+-------------+-------------+  y=12
|[F]FEDERER6 3|[F]DJOKOVIC 6|[F]ZVEREV   6|  (team1)
|[F]NADAL  4 6|[F]ALCARAZ  4|[F]RUUD     4|  (team2)
+-------------+-------------+-------------+  y=47
|COURT 4      |COURT 5      |COURT 6      |  (second row)
...
```

- Cell size: 106×48px (320÷3 ≈ 106, with 1px cell borders: 105px usable).
- At 106px cell width, name zone = ~60px → ~10 chars at FONT_S (6px wide). Score zone = ~40px.
- Name font: FONT_XS_SPLEEN (5px wide, 6px glyph) — same as M1.
- Score font: FONT_S_SPLEEN (6px wide) — same as M1.
- This is effectively M1-equivalent density packed into XL1.

**Pros:** 6 courts is a major capability upgrade for large tournament venues. All 6 courts visible at a glance. No font degradation compared to M1 — same fonts, just more courts.  
**Cons:** 106px cell width gives less name room than M1's 96px... wait — M1's W_MATCH is 96, XL1's 3-up cell is 106. That's actually wider per cell than M1. The font/content fits the same as M1 with marginally more room.  
The main trade-off: less impactful individual scores compared to the 2×2 layout. At 7m, FONT_XS (6px glyph) scores are barely legible. Best suited for closer-range tournament information panels (3–5m).  
**Backend data needed:** Extend `courts` array to up to 6 entries — already an array, no schema change.

---

### Proposal B: 2×2 Grid + Tournament Header Bar

**Concept:** Add a 16px header strip at the top (y=0..15) with tournament name and date. The 2×2 grid occupies y=16..95 — giving cells 40px height each (vs 48px in v1). Provides global tournament context.

```
+----------------------------------------+  y=0
|  SAARLAND OPEN 2026     QF — DAY 3     |  y=0..15 (header, FONT_S 8px glyph)
+========================================+  y=16 (COLOR_7C_GOLD divider)
+--------------------+--------------------+  y=17
|COURT 1      14:00  |COURT 2      14:30  |  y=17..25 (court names, 9px)
+--------------------+--------------------+  y=26
|[F] FEDERER  6 7 15 |[F] DJOKOVIC 3 6 40 |  y=27..38 (team1, 12px)
|[F] NADAL    4 5 30 |[F] ALCARAZ  6 4 30 |  y=39..50 (team2, 12px)
+--------------------+--------------------+  y=51
|COURT 3             |COURT 4             |  ...
```

- Header: y=0..15 (16px). Background: `COLOR_7C_DARK_BLUE` (37,56,73).
  - Tournament name: FONT_S_SPLEEN (8px glyph) at x=2, y=13. COLOR_WHITE.
  - Round/day: right-aligned, same font, COLOR_7C_GOLD.
  - Header divider: 1px at y=16 in COLOR_7C_GOLD.
- Grid cells (y=17..95, 79px total): each row = (79-1)÷2 = 39px.
  - H_MATCH = 39px. Court name strip = 9px (FONT_XS 6px + 3px). Team rows = 15px each.
  - Score font: FONT_S_SPLEEN (8px glyph) — just fits in 15px rows.

**Pros:** Tournament context is extremely useful for ITF events where multiple adjacent panels show different courts. Makes individual court panels part of a coherent information system. The gold divider is a strong visual anchor.  
**Cons:** Losing 16px from cell height (48→39) is a real cost — game score font downgrades from FONT_M to FONT_S, and team rows shrink from 17px to 15px. Name font remains FONT_XS. This erases most of the font upgrade gains from v1. Best suited for tournaments where panel context (which tournament, which round) is unknown to spectators — e.g. public venues, TV displays.  
**Backend data needed:** `tournament_name` and `round_name` fields on signage_info. These may already exist given the ITF use case.

---

### Proposal C: Per-Court Full-Width "Feature Match" Mode

**Concept:** When only 1 or 2 courts are active (common in finals), switch from 2×2 grid to a single-court or 2-row full-width layout where each match gets a full-width 320px strip.

**1 court active — full panel:**

```
+----------------------------------------+  y=0
|  COURT CENTRAL              QF          |  y=0..11 (header)
+----------------------------------------+  y=12
|  [FLAG]  FEDERER           6  7  3  15 |  y=13..52 (T1 row, 40px — FONT_L_SPLEEN)
+- - - - - - - - - - - - - - - - - - - -+  y=53
|  [FLAG]  NADAL             4  5  6  30 |  y=54..95 (T2 row, 42px — FONT_L_SPLEEN)
+----------------------------------------+
```

- Name font: `FONT_L_SPLEEN` (spleen-12x24, 15px glyph, 12px wide). Name width = ~20 chars. No truncation for most names.
- Score font: `FONT_XL_7SEGMENT` (44px glyph) for game score, `FONT_M_SPLEEN` (10px glyph) for set scores.
- This is essentially the scoreboard view (single match) reused in signage context — but rendered from signage-info data format.

**2 courts active — 2 full-width rows:**

```
+----------------------------------------+  y=0
|  CT1  [FLAG] FEDERER        6  7  3  15|  y=0..47 (40px per match, FONT_M_SPLEEN)
+- - - - - - - - - - - - - - - - - - - -+  y=47
|  CT2  [FLAG] DJOKOVIC       3  6  4  40|  y=48..95
+----------------------------------------+
```

Mode switching: if `len(courts) == 1` → full-panel single match. If `len(courts) == 2` → 2-row. If `len(courts) >= 3` → 2×2 grid (v1 layout).

**Pros:** Feature match mode is the most impactful XL1 layout for high-stakes matches. At finals, one match on the full 320×96 panel with 44px score digits is stunning. Mode switching is automatic and data-driven. Reuses score rendering logic from view_scoreboard.py.  
**Cons:** Requires a more complex layout dispatcher in view_signage.py — currently always renders 2×2. The signage data format (signage-info) is different from the scoreboard format (team1/team2) — the renderer would need to adapt.  
**Backend data needed:** No new fields — just render the existing signage-info `courts` array differently based on length. Client-side decision.
