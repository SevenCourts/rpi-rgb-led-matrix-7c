# XL1 Clock Layout

Idle mode: time-only display shown when no match is active and the clock variant is selected.

**Viewing mode:** Public, 7m+. The time must be readable immediately.  
**M1 reference:** `sevencourts/m1/view_clock.py`

---

## M1 Baseline (for reference)

On M1 (192×64):
- Default clock: `FONT_CLOCK_DEFAULT = FONT_XL_SDK` (texgyre-27, ~20px glyph).  
  Placed at x=120 (`W_LOGO_WITH_CLOCK`), y=62 (H_PANEL - 2). This leaves x=0..119 for a logo image.
- User-configurable clock: size (small/medium/large), font (font-1=7segment / font-2=spleen), alignment (h/v).
  - Small: `FONT_L_7SEGMENT` (26px) or `FONT_L_SPLEEN` (spleen-12x24, 24px)
  - Medium: `FONT_XL_7SEGMENT` (45px) or `FONT_XL_SPLEEN` (spleen-16x32)
  - Large: `FONT_XXL_7SEGMENT` (66px, fills M1's 64px height) or `FONT_XXL_SPLEEN` (spleen-32x64)
- `W_LOGO_WITH_CLOCK = 120` — used by view_clock.py and view_image.py to decide if a side-by-side logo+clock layout is possible.

---

## Section 1: v1 — Same Elements, Bigger Canvas

### Design Principle

The clock is the simplest view. v1 just needs:
1. An updated `W_LOGO_WITH_CLOCK` constant for XL1 — the wider panel means the clock can use a larger horizontal area, and a side logo can be given more space.
2. The "large" font (`FONT_XXL_7SEGMENT` at 66px glyph body) now fits vertically on XL1's 96px panel — on M1 this font technically overflowed by 2px (66 > 64). On XL1 it has 30px of vertical breathing room, so large clock mode becomes genuinely viable.
3. Horizontal centering math uses `W_PANEL = 320` — already dynamic in the code.

### Zone Map

No explicit zones — the clock fills the canvas. For the default (logo+clock) variant:

```
x=0          x=159  x=160           x=319
┌─────────────────┬──────────────────────┐  y=0
│                 │                      │
│   LOGO AREA     │     HH:MM            │
│   (160×96)      │  (7-segment clock)   │
│                 │                      │
└─────────────────┴──────────────────────┘  y=95
```

### Default Clock (logo+clock side-by-side variant)

When a logo image is shown alongside the clock (the `show_clock` path in `view_image.py`):

- Logo zone: x=0..159, full height 96px.
- Clock zone: x=160..319, full height 96px.
- Clock time string ("HH:MM") in `FONT_XXL_7SEGMENT` (66px glyph, char width ~45px).
  - "HH:MM" = 5 chars × 45px = 225px — exceeds the 160px clock zone.
  - **Use `FONT_XL_7SEGMENT` (44px glyph, char width ~28px) instead.**  
    "HH:MM" = 5 × 28 = 140px. Fits in 160px zone with 20px margin. Good.
  - x within clock zone: x = 160 + (160 - 140) // 2 = 160 + 10 = **x=170**.
  - y: `y_font_center(FONT_XL_7SEGMENT, 96)` = `(96 - 44) // 2 + 44 = 70`. Baseline y=**70**.

- `W_LOGO_WITH_CLOCK` for XL1: **160** (half the panel width). Update `dimens.py` or make view_clock.py reference W_PANEL.

### Full-Panel Clock (no logo, center-aligned)

When clock is shown with `h-align=center`, `v-align=center`:

- "Large" size: `FONT_XXL_7SEGMENT` (66px glyph, ~45px wide per char).
  - "HH:MM" = 5 × 45 = 225px. Centered: x = (320 - 225) // 2 = **48**.
  - y: `y_font_center(FONT_XXL_7SEGMENT, 96)`. Glyph body = 66px (from Y_FONT_SYMBOL_NORMAL_HEIGHTS). Wait — `FONT_XXL_7SEGMENT` has a glyph body of 64px per the lookup table (key: `FONT_XXL_7SEGMENT → 64`). On XL1 this fits with 32px of margin.  
    y = `(96 - 64) // 2 + 64 = 80`. Baseline y=**80**.
  - This is the headline variant — maximum impact at maximum distance.
- "Medium" size: `FONT_XL_7SEGMENT` (44px glyph).  
  - x = (320 - 5×28) // 2 = (320 - 140) // 2 = **90**.
  - y = (96 - 44) // 2 + 44 = **70**.
- "Small" size: `FONT_L_7SEGMENT` (25px glyph, ~18px wide per char).  
  - x = (320 - 5×18) // 2 = (320 - 90) // 2 = **115**.
  - y = (96 - 25) // 2 + 25 = **60**.

### Spleen Font Variants (font-2)

- "Large": `FONT_XXL_SPLEEN` (spleen-32x64, 40px glyph body, 32px char width).  
  On XL1 this is the correct large-clock font in Spleen family. "HH:MM" = 5×32 = 160px.
  - x-center = (320 - 160) // 2 = **80**.
  - y-center = (96 - 40) // 2 + 40 = **68**.
- "Medium": `FONT_XL_SPLEEN` (spleen-16x32, 20px glyph, 16px wide). "HH:MM" = 80px, x=**120**, y=**56**.
- "Small": `FONT_L_SPLEEN` (spleen-12x24, 15px glyph, 12px wide). "HH:MM" = 60px, x=**130**, y=**47**.

### ASCII Mockup — Full-panel large clock (1 char = 8px)

```
+----------------------------------------+
|                                        |  y=0..15
|                                        |
|       ██████  ██   ██████  ██████      |  y=16..47 (8-segment font)
|      ██   ██  ██   ██  ██  ██  ██     |
|      ██   ██  ██   ██████  ██████     |
|      ██   ██  ██      ██      ██      |
|       ██████  ██   ██████  ██████     |  y=~79 (baseline)
|                                        |  y=80..87
|                                        |
|                                        |
|                                        |
|                                        |  y=95
+----------------------------------------+
```

_FONT_XXL_7SEGMENT (64px glyph body), "HH:MM" centered at x=48, baseline y=80._

### Pixel Budget Summary

| Variant | Font | Glyph H | x start | x end | Vertical top | Baseline |
|---------|------|---------|---------|-------|-------------|---------|
| Large 7seg, center | FONT_XXL_7SEGMENT | 64px | 48 | 272 | 16 | 80 |
| Medium 7seg, center | FONT_XL_7SEGMENT | 44px | 90 | 230 | 26 | 70 |
| Small 7seg, center | FONT_L_7SEGMENT | 25px | 115 | 205 | 35 | 60 |
| Large Spleen, center | FONT_XXL_SPLEEN | 40px | 80 | 240 | 28 | 68 |
| Logo+clock default | FONT_XL_7SEGMENT | 44px | 170 | 310 | 26 | 70 |

All fit within 320×96. No overflow.

### Rationale

- `FONT_XXL_7SEGMENT` is the natural XL1 headline clock font. On M1 this font technically overflows (66px declared glyph vs. 64px panel) — it's listed as 64px in the lookup table (`FONT_XXL_7SEGMENT → 64`), suggesting it's been trimmed. Either way, on XL1's 96px it fits cleanly.
- `W_LOGO_WITH_CLOCK = 160` for XL1 is the natural value — exactly half the panel. The constant is currently hardcoded in `view_clock.py` and referenced by `view_image.py`. For XL1 abstraction, this should be moved to `dimens.py` as `W_LOGO_WITH_CLOCK = W_PANEL // 2`.
- All alignment computations in `view_clock.py` use `W_PANEL` and `H_PANEL` dynamically — no changes needed there except the `W_LOGO_WITH_CLOCK` constant.

### Open Questions

1. **`W_LOGO_WITH_CLOCK`**: Should this become `W_PANEL // 2` in dimens.py (dynamic) or remain a fixed constant per panel type? Current M1 value is 120 (not W_PANEL // 2 = 96), so it's been intentionally set wider. What logo aspect ratio is expected on XL1?
2. **`FONT_CLOCK_DEFAULT`**: The init screen and standby mode use `FONT_CLOCK_DEFAULT = FONT_XL_SDK` (texgyre-27). For XL1, upgrade to `FONT_XL_7SEGMENT` or `FONT_XXL_7SEGMENT`? Needs to be settable per panel type.

---

## Section 2: v2 Proposals

### Proposal A: Date + Day-of-Week Strip Below Clock

**Concept:** Show the current date below the clock time. Use the extra 32px of vertical space XL1 has over M1.

```
+----------------------------------------+
|                                        |  y=0..7
|                                        |
|         ██  ██:██  ██                  |  y=8..71 (large clock, FONT_XXL_7SEGMENT)
|                                        |
|                                        |
|        SATURDAY  24 MAY 2026           |  y=72..87 (date, FONT_M_SPLEEN 10px glyph)
|                                        |  y=88..95 (padding)
+----------------------------------------+
```

- Clock: `FONT_XXL_7SEGMENT` (64px glyph), x-centered, y=8..71 (baseline y=72).
- Date string: `FONT_M_SPLEEN` (spleen-8x16, 10px glyph, 8px wide). "SATURDAY 24 MAY 2026" = 20 chars × 8px = 160px. x = (320-160)//2 = **80**, y = baseline **84**.
- 1px separator at y=73 in COLOR_7C_DARK_GREY.

**Pros:** Date is genuinely useful on idle panels in club lobbies. 10px glyph (FONT_M_SPLEEN) is readable at ~4m — marginal but feasible for a lobby display. No backend data needed (client computes from time_now).  
**Cons:** Date text at 10px glyph barely meets the 7m readability threshold. Could use FONT_L_SPLEEN (15px glyph, 12px wide) — but "SATURDAY 24 MAY 2026" = 20 × 12 = 240px, still fits at 320px, centered at x=40. This is the better choice.  
**Backend data needed:** None — derivable from existing `time_now_in_TZ`.

---

### Proposal B: Split Clock + Weather

**Concept:** Left half = clock, right half = current weather (temperature + condition icon). Transforms the idle view from purely temporal to a useful lobby information panel.

```
+--------------------+--------------------+
|                    |       ☀            |  y=0..15
|    HH:MM           |  +23°C             |  y=16..71 (large clock left / temp right)
|                    |  Sunny             |  y=72..87
|                    |                    |  y=88..95
+--------------------+--------------------+
```

- Left half (x=0..159): clock in `FONT_XL_7SEGMENT` (44px glyph), centered horizontally at x=170 (within left half x-center = (160-140)//2 = 10, so x=10), baseline y=70.
- Right half (x=160..319):
  - Temperature: `FONT_XL_7SEGMENT` or `FONT_L_SPLEEN`, x=170..319, y-centered.
  - Condition text: `FONT_M_SPLEEN` (10px glyph) or `FONT_S_SPLEEN` (8px glyph). E.g. "Sunny", x=210, y=83.
  - Vertical separator at x=159.
- Temperature color: `COLOR_7C_BLUE` (cool) or `COLOR_7C_GOLD` (warm) based on temperature threshold.

**Pros:** Weather is a high-value idle screen element for outdoor club courts. The existing weather polling infrastructure (`_poll_weather_info()` in main.py and `weather_info` in PanelState) already provides this data — it's not used in the clock view today. This is low-hanging fruit.  
**Cons:** Condition text at 10px is only readable at ~3–4m. Temperature number in large font is fine. The "weather" data is already polled but currently only used in unspecified views — need to verify view_clock.py receives `weather_info`.  
**Backend data needed:** None new — `state.weather_info` already exists. View needs to accept it as a parameter.

---

### Proposal C: Full-Panel Logo + Animated Clock Pulse

**Concept:** Show the sponsor/club logo filling most of the panel, with a compact clock in the bottom-right corner. The XL1's extra height lets the logo breathe while the clock remains present.

```
+----------------------------------------+
|                                        |  y=0..3
|                                        |
|        [CLUB LOGO — 320×72px]          |  y=4..75
|                                        |
|                                        |
+- - - - - - - - - - - - - - - - - - - -+  y=76 separator
|                              HH:MM     |  y=77..95 (small clock, bottom-right)
+----------------------------------------+
```

- Logo: scaled to fit 320×72 while maintaining aspect ratio. Centered in zone.
- Clock: `FONT_L_7SEGMENT` (25px glyph, ~18px wide). "HH:MM" = 5×18 = 90px. x = 320 - 90 - 4 = **226**, baseline y=**94**.
- Clock color: `COLOR_GREY_DARKEST` (32,32,32) — deliberately dim so it doesn't compete with logo. Or `COLOR_7C_GOLD` for subtle brand touch.

**Pros:** Maximum logo impact. Useful for sponsor/tournament display during non-match hours. The logo zone at 320×72 is a dramatic improvement over M1's 192×44 (maximum logo area with bottom clock strip).  
**Cons:** Logo zone must accommodate non-square aspect ratios gracefully — needs careful centering. Clock at 25px glyph is on the edge of 7m readability. Better readability choice: `FONT_XL_7SEGMENT` in bottom strip, even if it takes 20px more vertical space (bottom strip y=76..95 = 19px — just barely fits 25px glyph with clipping, need y=71..95 = 24px strip for FONT_L_7SEGMENT cleanly).  
**Backend data needed:** None — same as current `draw_uploaded_image()` / `draw_preset_image()` flow.
