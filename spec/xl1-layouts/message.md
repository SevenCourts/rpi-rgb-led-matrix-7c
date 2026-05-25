# XL1 Message Layout

Idle mode: a text message (1–2 lines) fills the panel, optionally with a clock at bottom.

**Viewing mode:** Public, 7m+. Text is the entire content — font size is critical.  
**M1 reference:** `sevencourts/m1/view_message.py`

---

## M1 Baseline (for reference)

On M1 (192×64):
- Message zone: full panel width (192px), height = H_PANEL - 2 - 20 - 2 = 40px (reserves 24px for clock at bottom).
- 1-line message: `pick_font_that_fits(192, 40, text)` → tries FONT_L (15px), FONT_M (10px), FONT_S (8px). Text centered horizontally and vertically in the 40px zone.
- 2-line message: same font selection, each line gets 20px height. Centered within its half-zone.
- Clock (if requested): drawn at x=120, y=62 via `draw_clock(cnv, time_now, None)` — uses `FONT_CLOCK_DEFAULT` (texgyre-27, ~20px glyph).
- `COLOR_MESSAGE = COLOR_7C_BLUE` (111, 168, 220).

The clock check `if clock == True` (strict equality) means only a literal `True` value triggers the clock — a truthy dict would not.

---

## Section 1: v1 — Same Elements, Bigger Canvas

### Design Principle

On XL1 (320×96):
- The message zone is significantly larger — 320×72 if clock is reserved (vs 192×40 on M1). This means `pick_font_that_fits()` will almost always select FONT_XL (spleen-16x32, 20px glyph) on XL1, making messages dramatically larger and more readable at distance.
- The clock zone can also upgrade to a larger font.
- The `pick_font_that_fits()` function currently tries FONT_L, FONT_M, FONT_S. On XL1 it should try FONT_XL first. This requires either passing a custom font list or adding a panel-type-aware version.

### Zone Map (with clock)

```
y=0                           y=71  y=72  y=95
┌──────────────────────────────────┬────────────┐
│                                  │            │
│   MESSAGE ZONE (320×72)         │ (unused)   │
│   1–2 lines of text, centered    │            │
│                                  │            │
├──────────────────────────────────┤            │
│ (1px divider at y=72)            │            │
├──────────────────────────────────┤            │
│   CLOCK: HH:MM (right, y=73..95)│            │
└──────────────────────────────────┴────────────┘
```

Zone breakdown:
- **Message zone**: y=0..71, height=72px. Full width 320px.
- **Divider**: 1px at y=72, `COLOR_7C_DARK_GREY`. (On M1 there is no explicit divider — clock just overlaps the bottom.)
- **Clock strip**: y=73..95, height=23px. Clock drawn baseline y=93.

Clock font: `FONT_L_7SEGMENT` (25px glyph) — glyph top = y=93-25 = 68. But that extends into the message zone. Use `FONT_M_SPLEEN` (spleen-8x16, 10px glyph) instead for the clock in message mode, or push clock baseline to y=95 using `FONT_L_7SEGMENT` (25px) with baseline at y=95 → glyph top = y=70 which is 2px below the divider. Acceptable.

Actually: `FONT_L_7SEGMENT` baseline y=95, glyph occupies y=70..95 (25px). The divider is at y=72. The clock glyph starts at y=70, 2px above the divider — it would overlap. **Use y=95 but place divider at y=69 to give the clock 26px strip (y=70..95)**. Then message zone = y=0..68, height=69px. Still generous.

Revised zones:
- **Message zone**: y=0..68, height=69px.
- **Divider**: y=69.
- **Clock strip**: y=70..95, height=26px.
  - Clock font: `FONT_L_7SEGMENT` (25px glyph), "HH:MM" = 5×18 = 90px.
  - Clock x: right-aligned, x = 320 - 90 - 4 = **226**. y=**95** (baseline).
  - Clock color: `COLOR_GREY_DARK` (96,96,96) — subdued so it doesn't compete with the message.

### Zone Map (without clock)

Full panel is the message zone: y=0..95, 320×96. Text centered.

### Font Selection for Message Text

`pick_font_that_fits(320, 69, text)` with FONT_XL added as first candidate:

| Font | Glyph H | Char W | Max chars @ 320px | Fits in 69px? |
|------|---------|--------|-------------------|---------------|
| FONT_XL (spleen-16x32) | 20px | 16px | ~20 | Yes |
| FONT_L (spleen-12x24) | 15px | 12px | ~26 | Yes |
| FONT_M (spleen-8x16) | 10px | 8px | ~40 | Yes |
| FONT_S (spleen-6x12) | 8px | 6px | ~53 | Yes |

For a 2-line message, each line gets 69//2 = **34px**. FONT_XL (20px) fits in 34px. FONT_L (15px) also fits. Both are good at 7m.

For a 1-line message, the full 69px is available. Could use `FONT_XXL_SPLEEN` (spleen-32x64, 40px glyph, 32px wide) for extreme impact. "WELCOME" = 7 × 32 = 224px — fits in 320px. y = y_font_center(FONT_XXL_SPLEEN, 69) = (69-40)//2 + 40 = **54**.

### ASCII Mockup — 1-line message (1 char = 8px)

```
+----------------------------------------+
|                                        |  y=0..7
|                                        |
|         WELCOME                        |  y=8..55 (FONT_XXL_SPLEEN, 40px glyph)
|                                        |
|                                        |
|                                        |
|                                        |
+========================================+  y=69 divider
|                           14:30        |  y=70..95 (clock, FONT_L_7SEGMENT)
+----------------------------------------+
```

### ASCII Mockup — 2-line message (1 char = 8px)

```
+----------------------------------------+
|                                        |  y=0..3
|      MATCH STARTS                      |  y=4..27 (FONT_XL, 20px glyph)
|                                        |
|        IN 10 MINUTES                   |  y=28..51 (FONT_XL, 20px glyph)
|                                        |
|                                        |
|                                        |
|                                        |
+========================================+  y=69 divider
|                           14:30        |  y=70..95
+----------------------------------------+
```

### Pixel Budget

| Element | x | y (baseline) | w | h | Font |
|---------|---|-------------|---|---|------|
| 1-line msg (XXL) | x_center | 54 | 224 | 40 | FONT_XXL_SPLEEN |
| 1-line msg (XL) | x_center | 58 | varies | 20 | FONT_XL_SPLEEN |
| 2-line msg row 1 | x_center | y_font_center(font, 34) | varies | varies | pick_font_that_fits |
| 2-line msg row 2 | x_center | 34 + y_font_center(font, 34) | varies | varies | same |
| Divider | 0 | 69 | 320 | 1 | — |
| Clock | 226 | 95 | 90 | 25 | FONT_L_7SEGMENT |

All fit within 320×96. No overflow.

### Changes from M1

| Aspect | M1 | XL1 v1 |
|--------|----|--------|
| Message zone height | 40px | 69px |
| Message zone width | 192px | 320px |
| Primary font (1-line) | FONT_L or FONT_M | FONT_XXL_SPLEEN or FONT_XL |
| Clock font | FONT_XL_SDK (texgyre-27) | FONT_L_7SEGMENT (25px) |
| Clock x position | x=120, right of logo area | x=226, right-aligned |
| Clock y (baseline) | 62 | 95 |
| Clock color | COLOR_WHITE (default) | COLOR_GREY_DARK (subdued) |

### Rationale

- The message zone height nearly doubles on XL1 (40→69px), enabling FONT_XXL_SPLEEN (40px glyph) for a single-line message — producing letters ~20px taller than the largest M1 option. At 7m+ this is a genuine improvement.
- Clock is intentionally subdued (`COLOR_GREY_DARK`) in the message view because the message is primary. The clock is supporting information.
- Divider at y=69 (rather than the M1 approach of just overlapping) makes the layout explicit and avoids any message text drifting into the clock strip.

### Open Questions

1. **`pick_font_that_fits()` on XL1**: Currently this function tries FONT_L, FONT_M, FONT_S. For XL1 it should try FONT_XL first. Two options: (a) add FONT_XL to the candidate list and make it panel-type-aware; (b) pass a font list as a parameter. Option (b) is more flexible and avoids global state changes.
2. **Clock x position**: M1 places the clock at `W_LOGO_WITH_CLOCK = 120`. On XL1 the message fills the full width, so the clock position should be purely right-aligned (not tethered to a logo zone). The `draw_clock(cnv, time_now, None)` path uses `W_LOGO_WITH_CLOCK` as the clock x — this would need to change for XL1 when called from the message view.
3. **Single-line font ceiling**: Should the message view attempt FONT_XXL_SPLEEN (40px glyph) on XL1 for single short messages, or cap at FONT_XL (20px) for consistency? The larger font is more impactful but may look oversized for longer messages.

---

## Section 2: v2 Proposals

### Proposal A: Message + Icon/Emoji Strip

**Concept:** A 32×32px icon (from a small icon font or preset pixel-art set) sits to the left of the message text, providing a visual anchor. Uses the extra horizontal width XL1 has.

```
+----------------------------------------+
|      |                                 |
| [32] |   COURT AVAILABLE               |  y=0..47
|      |                                 |
+- - - +- - - - - - - - - - - - - - - - -+  divider
|      |                                 |
| [32] |   BOOK NOW: 0711-123456         |  y=49..95
|      |                                 |
+----------------------------------------+
```

- Icon zone: x=0..39 (32px icon + 8px padding), full height. Contains a 32×32 or 24×24 pixel-art icon (tennis ball, clock, info symbol, etc.).
- Message zone: x=40..319, 280px wide.
- Font: `pick_font_that_fits(280, 47, line)` — FONT_XL (20px) fits comfortably.
- Icons would be a small fixed set (court_available, booking, info, warning) stored as pixel matrices, similar to the existing service ball and trophy in view_scoreboard.py.

**Pros:** Visual icons dramatically increase parse speed — a viewer recognizes "tennis ball = court available" before reading. 280px text width is still ~17 chars at FONT_XL — enough for most short messages. Low backend cost: just an optional `icon` field in idle_info.  
**Cons:** Requires building a small icon library. Icon rendering at 32×32 is manageable with pixel matrix arrays (same pattern as the 7×7 service ball). Icons must be meaningful at distance — filled shapes work better than outlines.  
**Backend data needed:** Optional `icon` enum field in `idle_info` (e.g., "tennis_ball", "clock", "info", "checkmark").

---

### Proposal B: Message + QR Code

**Concept:** Reserve the right 96×96 px of the panel for a QR code (a 96×96 module renders a ~V3 QR at ~2.4px per module). The message text occupies the left 224×96. This turns an idle screen into a call-to-action.

```
+-------------------------------+---------+
|                               |         |
|  BOOK ONLINE:                 |  [QR]   |
|  sevencourts.com              |  96×96  |
|                               |         |
+-------------------------------+---------+
```

- QR zone: x=224..319, y=0..95. 96×96px exactly.
  - A QR v2 (25×25 modules) at 96px = 3.8px per module — marginal but scannable at ~0.5m. A QR v1 (21×21 modules) at 96px = 4.6px per module — better.
  - QR code generated by a library (e.g. `qrcode` Python package), rendered as a Pillow Image at 96×96, then placed with `canvas.SetImage()`.
  - Color: white modules on black background (no inversion).
- Message zone: x=0..223, 224px wide.
- Font: `pick_font_that_fits(224, 96, line1, line2)` — FONT_XXL_SPLEEN (40px glyph, 32px wide) fits for short messages; "BOOK ONLINE:" = 12 × 32 = 384px — too wide. FONT_XL (16px wide): "BOOK ONLINE:" = 12×16 = 192px ≤ 224px. Good for 2-line messages.
- Vertical separator: x=223, `COLOR_7C_DARK_GREY`.

**Pros:** High-value engagement for clubs with online booking. The QR code is the element that makes XL1 worth the upgrade — M1 has no viable QR zone. Self-describing (text + scannable link). No printing needed.  
**Cons:** Requires `qrcode` library addition to dependencies. QR readability at 96px is fine for close-range scanning (~0.5–1m) — viewers would need to approach the panel. Not readable at 7m (wrong use case for QR). `url` field needed in idle_info.  
**Backend data needed:** `qr-url` string field in `idle_info`. The QR is generated client-side from this URL.

---

### Proposal C: Scrolling Ticker + Static Message

**Concept:** Static primary message occupies the top 72px, a horizontally scrolling text ticker runs in the bottom 22px. The ticker cycles through multiple secondary messages (e.g. court schedules, club announcements) automatically.

```
+----------------------------------------+
|                                        |
|      WELCOME TO                        |  y=0..71 (static primary, FONT_XL_SPLEEN)
|      VAIHINGEN-ROHR                    |
|                                        |
|                                        |
+========================================+  y=72 divider
| ←  Court 1: Müller vs. Schmidt  14:30  |  y=73..94 (ticker, FONT_XS 6px glyph)
+----------------------------------------+
```

- Static zone: y=0..71, same as message view above.
- Ticker strip: y=73..94, height=22px.
  - Text in `FONT_XS` (spleen-5x8, 6px glyph). Horizontally scrolled pixel-by-pixel each render frame.
  - Ticker offset stored in PanelState (or derived from time_now for simplicity: pixel offset = (seconds × 5) mod total_text_width).
  - Color: `COLOR_7C_GOLD` for ticker text on black background.
  - Maximum ticker text: no limit — text wraps around continuously.
- Primary message: same font selection as main message view (FONT_XXL_SPLEEN or FONT_XL).

**Pros:** Ticker is a genuinely different use case from the existing 2-line message. Useful for clubs that want to show a welcome message plus a stream of court schedules or club news. No architectural changes needed for the static zone. Ticker can be computed from time_now without blink state if time-based.  
**Cons:** Scrolling requires the render loop to redraw every frame (every 1s currently). A ticker that scrolls at 5px/s would need a much faster render loop (>10fps minimum). This conflicts with the current 1s render interval unless the render loop is updated to run at a higher tick rate for ticker mode. This is a significant firmware change. Alternatively: a slow ticker that advances one "position" per second is simpler but doesn't look smooth.  
**Backend data needed:** `ticker-messages` list of strings in `idle_info`. Ticker text assembled client-side by joining with " • " separator.
