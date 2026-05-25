# XL1 Scoreboard Layout

Live tennis match display. The densest and most critical layout — this is what players, coaches, and spectators look at during a match.

**Viewing mode:** Public, 7m+. Every primary element must be readable at distance.  
**M1 reference:** `sevencourts/m1/view_scoreboard.py`

---

## M1 Baseline (for reference)

On M1 (192×64):
- Panel split horizontally at y=32 — Team 1 top half, Team 2 bottom half.
- Name zone: x=0 to ~x=155 (flag + name). `pick_font_that_fits()` selects FONT_L (spleen-12x24, 15px glyph) or smaller.
- Score zone: x=96 onward (`X_MIN_SCOREBOARD = W_PANEL // 2 = 96`).
  - Set columns: each 20px wide (`W_SCORE_SET = 20`), placed RTL.
  - Game score column: x=163 (`X_SCORE_GAME`).
  - Service ball icon (7×7): x=155 (`X_SCORE_SERVICE`).
  - Score font: `FONT_XL_SDK` (texgyre-27, ~20px glyph body).
- Flags: 18×12px, vertically centered in team's half.

---

## Section 1: v1 — Same Elements, Bigger Canvas

### Design Principles

XL1 is 320×96 — **67% wider and 50% taller** than M1. The key opportunity in v1 is:
1. Upgrade the name font: FONT_L_SDK (10x20) → FONT_XL (spleen-16x32, 20px glyph) for singles names.
2. Upgrade the score font: FONT_XL_SDK (texgyre-27) → FONT_XXL_7SEGMENT (7segment_66, 64px glyph) — fills the full panel height, immediately readable at 15m+.
3. Widen the name column to use freed-up pixel budget from the wider panel.
4. Keep the same logical structure: left = names, right = scores, horizontal split = teams.

### Zone Map

```
y=0  ────────────────────────────────────────
     TEAM 1: name zone (left) | score zone (right)
y=47 ────────────────────────────────────────  ← 1px divider
y=48 ────────────────────────────────────────
     TEAM 2: name zone (left) | score zone (right)
y=95 ────────────────────────────────────────
```

Each team occupies exactly 47px of height (y=0..46 for T1, y=48..94 for T2), with a 1px divider at y=47.

The score zone uses `FONT_XXL_7SEGMENT` (66px glyph body). Since each team half is 47px, the 66px digit cannot fit in one half. **Therefore: use `FONT_XL_7SEGMENT` (44px glyph body) for the score font.** This fills each 47px half nicely (44px glyph + 3px breathing room top/bottom, centered with y_font_center).

### Score Column Layout (right side, x=200 onward)

The right 120px (x=200..319) contains the score zone. This is wider than M1's score zone (~37px for 3 sets + game), enabling larger digits and more comfortable set column spacing.

```
x=200          x=252      x=280   x=307 x=316
 |  set1 (24px) | set2(24) | set3(24) | game(26) |
```

Set columns: 24px wide each (up from M1's 20px), supports 2-digit scores in FONT_M_SPLEEN (8x16, fits in 24px cell with centering).
Game score column: x=280, width=26px, using `FONT_XL_7SEGMENT` (44px, width ~28px per digit).

Actually reconsidering for clarity — the score zone uses a single large font throughout. Let's use `FONT_XL_7SEGMENT` (44px glyph, char width ~28px) for game scores and `FONT_L_SPLEEN` (spleen-12x24, 24px glyph, 12px wide) for set scores. This mirrors M1's pattern of large game + smaller set digits.

**Revised score zone (x=192..319, width=128px):**

```
x=192   x=236    x=260    x=284   x=291       x=319
 |  set1  |  set2  |  set3  | srv | game score  |
  (24px)   (24px)   (24px)  (7px)   (28px)
```

- Set score columns: each 24px wide, centered digit in `FONT_L_SPLEEN` (spleen-12x24, glyph 15px, char 12px).
- Service ball icon: 7×7px pixel art at x=284, y=centered in team half.
- Game score: `FONT_XL_7SEGMENT` (44px glyph), x=291 for 2-char value, x=305 for 1-char value (right-aligned within 29px column).
- Score area background fill: `COLOR_BLACK` — same pattern as M1 to prevent name text bleeding into score zone.

**X_MIN_SCOREBOARD for XL1 = 192** (= 320 // 2 + 32, giving names 192px). Alternatively, keep it at exactly `W_PANEL // 2 = 160` for simplicity. **Recommended: x=160**, giving names 160px and scores 160px — a clean 50/50 split.

With x=160 as the score zone start:

```
x=160    x=208    x=232    x=256    x=263         x=319
 | set1   | set2   | set3   | srv   | game score    |
  (24px)   (24px)   (24px)  (7px)    (56px)
```

Game score column width = 56px comfortably fits 2-digit `FONT_XL_7SEGMENT` chars (28px each).

When only 1 set: set1 at x=208 (right-aligned within the 3-column space), sets 2&3 empty.  
When 2 sets: set1 at x=208, set2 at x=232.  
When 3 sets: set1 at x=160, set2 at x=208, set3 at x=232.  
(This mirrors M1's RTL packing logic with adjusted x values.)

### Name Zone (x=0..159, width=160px)

- Flag images: keep at 18×12px (current W_FLAG × H_FLAG), placed at x=0, y=centered in team half.  
  Future: consider 24×16px flags on XL1 for better readability (open question — see below).
- Name text: x = W_FLAG + 2 = 20.
- Available name width: 160 - 20 - 3 (MARGIN) = 137px.
- Available name height: 47px (team half height).
- Font selection for singles: `pick_font_that_fits(137, 45, name)` — with FONT_XL (spleen-16x32, 20px glyph, 16px wide) added as first candidate. A 137px-wide zone fits ~8 chars at 16px — sufficient for most last names.  
  Fallback: FONT_L (spleen-12x24, 15px glyph) → ~11 chars. Then FONT_M, FONT_S.
- For doubles: 4 names across 4 rows in 96px → name height per player = ~22px → FONT_L (15px glyph) fits.

### ASCII Mockup (1 char = 8px, 40 cols × 12 rows)

Singles, 3 sets in progress:

```
+----------------------------------------+
|[FLG] FEDERER               | 6  7  3 15|
|                            |           |
|                            |  (ball) 40|
|                            |           |
|                            |           |
+--------------------------------------------+  <- divider y=47
|[FLG] NADAL                 | 4  5  6 30|
|                            |           |
|                            |           |
|                            |           |
|                            |           |
+----------------------------------------+
```

Actual pixel positions (singles, 3 sets):

| Element | x | y (baseline or top) | Font | Color |
|---------|---|---------------------|------|-------|
| T1 flag | 0 | 17 (centered in y=0..46) | — | — |
| T1 name | 20 | y_font_center(font, 47) | pick_font_that_fits | COLOR_WHITE |
| T2 flag | 0 | 64 (centered in y=48..94) | — | — |
| T2 name | 20 | 48 + y_font_center(font, 47) | pick_font_that_fits | COLOR_WHITE |
| Divider line | 0..319 | 47 | — | COLOR_7C_DARK_GREY |
| Score background | x=157..319 | y=0..95 | — | COLOR_BLACK |
| T1 set1 digit | 160 | y_font_center(FONT_L, 47) | FONT_L_SPLEEN | COLOR_WHITE/GREY |
| T1 set2 digit | 184 | same | FONT_L_SPLEEN | COLOR_WHITE/GREY |
| T1 set3 digit | 208 | same | FONT_L_SPLEEN | COLOR_WHITE/GREY |
| T1 service ball | 236 | 20 (y_center of 0..46) | pixel art 7×7 | COLOR_YELLOW |
| T1 game score | 245 | y_font_center(FONT_XL_7SEGMENT, 47) | FONT_XL_7SEGMENT | COLOR_WHITE |
| T2 set1 digit | 160 | 48 + y_font_center(FONT_L, 47) | FONT_L_SPLEEN | COLOR_WHITE/GREY |
| T2 game score | 245 | 48 + y_font_center(FONT_XL_7SEGMENT, 47) | FONT_XL_7SEGMENT | COLOR_WHITE |
| Status dot | 316 | 92 | 4×4 pixel art | COLOR_7C_STATUS_ERROR |

### Pixel Budget Validation

- Vertical: 47 + 1 (divider) + 47 = **95px** (fits in 96px, 1px spare at bottom — status dot sits at y=92 safely).
- Horizontal name zone: flag (18px) + gap (2px) + name (~8–11 chars at 16–12px) = 20 + 112–132px ≤ 160px. OK.
- Horizontal score zone (per team): set1+set2+set3 = 3×24px = 72px, service = 7px, game = ~56px → total ~135px within 160px zone. Comfortable.

### Vertical Centering Formulas

- `y_font_center(FONT_XL_7SEGMENT, 47)`:  
  FONT_XL_7SEGMENT glyph body = 44px. `(47 - 44) // 2 + 44 = 45`. Baseline y=45 for T1, baseline y=93 for T2. (Glyph body top = y=1 for T1, y=49 for T2.)
- `y_font_center(FONT_L_SPLEEN, 47)`:  
  Glyph body = 15px. `(47 - 15) // 2 + 15 = 31`. Baseline y=31 for T1, y=79 for T2.

### Win/loss color convention

- Won set digit: `COLOR_WHITE` (255,255,255)
- Lost set digit: `COLOR_GREY` (192,192,192)
- Game score: `COLOR_WHITE`
- Service ball: `COLOR_YELLOW` (255,255,0)

### Trophy icon (winner indicator)

Current M1 trophy is 9×10px. On XL1 it can remain the same size — scale doesn't justify redesigning. Place at same relative position: x=236, y_center of winning team's half.

### Rationale

- **50/50 horizontal split** is the cleanest division for a larger panel. M1 used 96/96 (exact half). XL1 is wider — same half-split at x=160 gives names a generous 160px budget without the score zone feeling cramped.
- **FONT_XL_7SEGMENT for game score** at 44px glyph is the maximum that fits in a 47px team half. 7-segment style is unambiguous for sport scores at distance.
- **FONT_L_SPLEEN for set scores** (12x24, 15px glyph, 12px wide) gives a clear visual hierarchy: the dominant game score is ~3× the height of set scores.
- **Horizontal divider at y=47** replaces M1's implicit split. Adds 1px of visual separation that helps parse T1 vs T2 at distance.

### Constraints and Trade-offs

- **3-set maximum**: Same as M1 — 5-set matches not yet supported. 3 columns × 24px = 72px fits easily. If 5-set support is added, the score zone math changes.
- **Match-tie-break display**: Same crutch as M1 (detecting MTB by score ≥ 10). No change needed in v1.
- **Doubles**: Name zone height per player = ~22px (96px ÷ 4 names + divider). FONT_L (15px glyph) fits. Name truncation to MAX_LENGTH_NAME_DOUBLES (3 chars) is unchanged but could be relaxed to 5–6 chars given the wider zone — open question.
- **`isTotalPointsMatch` (Americano)**: Set digits are suppressed; only game/total-points score shown. Layout degrades gracefully since set columns are just blank.

---

## Section 2: v2 Proposals

### Proposal A: Match Clock + Momentum Bar

**Concept:** Add a thin strip at the very top (y=0..7, 8px tall) showing match elapsed time (left) and a simple momentum indicator (right). The main 47/47 split moves down to y=9..55 / y=57..95, divider at y=56.

```
+----------------------------------------+
|01:23:45                     ====>      |  <- y=0..7 (clock + momentum, FONT_XS 6px glyph)
+- - - - - - - - - - - - - - - - - - - -+  <- y=8 separator
|[FLG] FEDERER        | 6  7  3       15|  <- y=9..55
| - - - - - - - - - - + - - - - - - - -|  <- y=56 divider
|[FLG] NADAL          | 4  5  6       30|  <- y=57..95
+----------------------------------------+
```

- Match clock: `HH:MM:SS` in `FONT_XS` (5px glyph, 5px wide) at x=2, y=6.
- Momentum bar: x=100..316, y=4. A horizontal bar 216px wide, split at center. Left portion = T1 color, right portion = T2 color, relative length = fraction of games won. E.g. T1 won 60% → T1 bar = 130px, T2 bar = 86px.
- Team halves shrink from 47px to 46px each — negligible impact; FONT_XL_7SEGMENT (44px glyph) still fits with 1px margin.

**Pros:** Match duration is the most-requested piece of secondary data. Momentum bar is visually compelling and parse-at-a-glance. Requires no layout refactor — just a new top strip.  
**Cons:** Match clock data needs server support (start timestamp → elapsed). Momentum bar requires per-match game win counts (already in setScores, can be computed client-side). Strip at 8px uses FONT_XS — marginal at 7m, but this is secondary info, not primary.  
**Backend data needed:** Match start timestamp (or elapsed seconds). Game win counts are derivable from existing set score data.

---

### Proposal B: Court Identity Header + Wider Name Column

**Concept:** Add a 14px header strip (y=0..13) showing court name and match round/tournament name. This anchors context for spectators who walk past multiple courts. Scores move to y=15..95 (40px per team half).

```
+----------------------------------------+
| COURT 3                    QF - ROUND 1|  <- y=0..13, FONT_S (8px glyph)
+========================================+  <- y=14, 1px divider (COLOR_7C_GOLD)
|[FLG] FEDERER          | 6  7  3     15|  <- y=15..54 (40px)
|- - - - - - - - - - - -+- - - - - - - -|  <- y=55 divider
|[FLG] NADAL            | 4  5  6     30|  <- y=56..95 (40px)
+----------------------------------------+
```

- Court name: `FONT_S` (spleen-6x12, 8px glyph) at x=2, y=13. COLOR_GREY.
- Round/tournament: right-aligned in same font, COLOR_7C_GOLD.
- Header background: `COLOR_7C_DARK_BLUE` (37,56,73) — distinguishes it from black name zone.
- Name zone available height reduced to 39px. FONT_XL (20px glyph) still fits easily; even FONT_XXL_SPLEEN (40px) just barely fits.
- Score font: FONT_XL_7SEGMENT (44px) now exceeds 39px. **Downgrade to FONT_L_7SEGMENT (25px glyph)**. This reduces score size; mitigated by the fact that XL1 is physically larger.

**Pros:** Court ID + round context is instantly useful at tournaments. Header background (dark blue) provides strong visual framing that helps people identify their specific court's panel among many.  
**Cons:** Score font downgrade from 44px → 25px glyph is a real trade-off — game scores become less dominant. For dedicated single-court panels, the court name is often already known, making this header redundant.  
**Backend data needed:** `court_name` and `round_name` fields on the match object. These may already exist in the signage-info schema.

---

### Proposal C: Ace / Double-Fault Counters

**Concept:** Use the extra 128px of width vs M1 to add a narrow stats strip on the far right (x=280..319, width=40px). This strip shows ace count (A) and double-fault count (DF) for each player, in small type. The main score zone shifts left and narrows to x=160..279 (120px).

```
+----------------------------------------+
|[FLG] FEDERER      | 6  7  3  40 | A:12 |  <- A (aces) for T1
|                   |             |DF: 3 |  <- DF for T1
+- - - - - - - - - -+- - - - - - -+- - -+
|[FLG] NADAL        | 4  5  6  30 | A: 8 |  <- A for T2
|                   |             |DF: 5 |  <- DF for T2
+----------------------------------------+
```

- Stats strip: x=280, width=40px. Two rows per team half: "A:NN" and "DF:N".
- Font: `FONT_XS` (5px glyph, 5px wide) — fits "DF: 9" (6 chars × 5px = 30px ≤ 40px). These stats are supplementary; FONT_XS is acceptable since they're not the primary message.
- Stats label color: `COLOR_7C_GOLD` for aces (celebratory), `COLOR_GREY_DARK` for DFs (negative).
- Vertical divider at x=279 separating stats strip from score zone.
- Score zone (x=160..279, 120px): same set+game layout but game column narrows to 38px. Still fits `FONT_XL_7SEGMENT` 1-digit numbers; 2-digit numbers (15, 40, Ad) might need to use `FONT_L_7SEGMENT` (25px). Alternatively, use `FONT_L_7SEGMENT` for game throughout, keeping sets in FONT_M_SPLEEN.

**Pros:** Ace count is a fan favorite — very high engagement at professional/semi-pro events. The 2-column vertical layout within the stats strip makes excellent use of the pixel budget. No change to the dominant score area.  
**Cons:** Requires server to push per-player ace/DF stats in real time. At 5px glyph the stats are only readable up close (~3m) — this is supplementary info not critical for distant viewers. Risk of clutter if match just started and all counts are zero.  
**Backend data needed:** Per-player `aces` and `doubleFaults` integer fields on team/player objects. Not currently in the match response schema (best guess).
