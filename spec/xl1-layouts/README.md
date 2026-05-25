# XL1 Layout Specifications

## Panel Dimensions

| Panel | Resolution | Physical panels |
|-------|-----------|-----------------|
| M1    | 192 × 64  | Three 64×64 HUB75 chained |
| XL1   | 320 × 96  | Five 64×64 HUB75 chained |

XL1 has 30,720 px² total vs. M1's 12,288 px² — **2.5× more real estate**.

---

## ASCII Mockup Scale Convention

All mockups in these specs use **1 character = 8 pixels** (both horizontal and vertical).

- Grid width: 320 ÷ 8 = **40 chars**
- Grid height: 96 ÷ 8 = **12 rows**

Each grid cell represents an 8×8 pixel block. Coordinates given alongside mockups are always in **actual pixels**, not grid units.

---

## Available Fonts (from rgbmatrix.py)

| Alias | File | Char W | Glyph H | Max chars @ 320px |
|-------|------|--------|---------|-------------------|
| FONT_XXS / tom-thumb | tom-thumb.bdf | ~4px | 5px | ~80 |
| FONT_XS | spleen-5x8.bdf | 5px | 6px | ~64 |
| FONT_S | spleen-6x12.bdf | 6px | 8px | ~53 |
| FONT_M | spleen-8x16.bdf | 8px | 10px | ~40 |
| FONT_L | spleen-12x24.bdf | 12px | 15px | ~26 |
| FONT_XL | spleen-16x32.bdf | 16px | 20px | ~20 |
| FONT_XXL_SPLEEN | spleen-32x64.bdf | 32px | 40px | ~10 |
| FONT_L_SDK | 10x20.bdf | 10px | 13px | ~32 |
| FONT_XL_SDK | texgyre-27-modified.bdf | ~17px | 20px | ~18 |
| FONT_L_7SEGMENT | 7segment_26 | 18px | 25px | ~17 |
| FONT_XL_7SEGMENT | 7segment_45 | 28px | 44px | ~11 |
| FONT_XXL_7SEGMENT | 7segment_66 | 45px | 64px | ~7 |

**Viewing distance for XL1:** Assumed same as M1 (7m+ public, 1–3m admin).  
**Minimum public font:** FONT_L (spleen-12x24, 15px glyph height) — up from FONT_L_SDK (10x20) on M1, because the panel is physically larger and viewers will stand further.

---

## Color Constants (from rgbmatrix.py)

```
COLOR_WHITE     = (255, 255, 255)
COLOR_GREY      = (192, 192, 192)
COLOR_GREY_DARK = ( 96,  96,  96)
COLOR_YELLOW    = (255, 255,   0)
COLOR_7C_BLUE   = (111, 168, 220)   # brand blue
COLOR_7C_GOLD   = (241, 194,  50)   # brand amber
COLOR_7C_GREEN  = (147, 196, 125)   # brand green
COLOR_7C_DARK_GREY  = ( 23,  23,  23)
COLOR_7C_DARK_GREEN = ( 58,  77,  49)
COLOR_7C_DARK_BLUE  = ( 37,  56,  73)
COLOR_7C_STATUS_ERROR = COLOR_7C_BLUE
COLOR_7C_STATUS_INIT  = COLOR_7C_GREEN
COLOR_7C_STANDBY      = COLOR_7C_DARK_GREEN
```

---

## Common Positioning Principles

### Status-indicator dot (top-level dispatcher, view.py)

On M1 the status dot is a 4×4 circle pixel-art drawn at `(W_PANEL - 4, H_PANEL - 4)` — i.e. bottom-right corner.

On XL1 the same logic applies: dot at `(316, 92)` (i.e. `(W_PANEL - 4, H_PANEL - 4)` with W=320, H=96). The code in `view.py` already uses `W_PANEL` and `H_PANEL` constants from `dimens.py`, so this will work automatically once `dimens.py` returns 320/96 for XL1.

The standby dot is 2×2, placed at `(W_PANEL - 3, H_PANEL - 3)` — same dynamic formula.

### Daemon status overlay (view_daemon_status.py)

The overlay is anchored top-left at `(2, 2)`. Its box width is constrained by content. Nothing in its layout is relative to W_PANEL or H_PANEL except `_MIN_BOX_H = H_PANEL // 2`. On XL1, `_MIN_BOX_H` becomes 48px (vs 32px on M1) — this may make the overlay slightly taller on XL1 which is acceptable.

### Zone naming convention used in these specs

```
Header  y=0  … y=(H-1) of header strip  (optional in some views)
Main    y=…  … y=(H-1) of main zone
Footer  y=…  … y=95
```

Dividers are 1px horizontal lines in `COLOR_7C_DARK_GREY`.

---

## View Spec Files

| View | File | Description |
|------|------|-------------|
| Scoreboard | [scoreboard.md](scoreboard.md) | Live tennis match (primary use case) |
| Clock | [clock.md](clock.md) | Idle clock display |
| Image | [image.md](image.md) | Idle promotional image |
| Message | [message.md](message.md) | Idle text message |
| Signage | [signage.md](signage.md) | Multi-court ITF tournament overview |

---

## Open Questions for Implementation

See each spec file for view-specific questions. Cross-cutting questions:

1. **Flag images:** Current flag images are 18×12px (W_FLAG × H_FLAG). On XL1 should they be scaled up? If so, what target size? The PIL `.thumbnail()` call in `view_signage.py` supports this, but `view_scoreboard.py` uses `canvas.SetImage()` directly without scaling. A `W_FLAG_XL1` constant in `dimens.py` would be the right place to define this.

2. **`pick_font_that_fits()`:** Currently tries FONT_L, FONT_M, FONT_S in that order. On XL1 the available area is larger, so FONT_XL should be added as the first candidate. Needs a new XL1-aware version of this function or a parameter to pass the candidate list.

3. **`FONT_CLOCK_DEFAULT`:** Currently `FONT_XL_SDK` (texgyre-27). For XL1 the natural default is `FONT_XL_7SEGMENT` (45px tall, uses full height on M1, needs vertical centering on XL1's 96px). This constant may need to be panel-type-aware.

4. **`W_LOGO_WITH_CLOCK`:** Hard-coded at 120px in `view_clock.py`. On XL1 the left zone for a logo alongside the clock should be wider — suggest 160px, but depends on what logo/image is used.

5. **XL1 hardware refresh rate:** The 5-panel chain reduces refresh rate vs M1's 3-panel chain. See `spec/l1-chain-length-refresh-rate.md` for context. Confirm acceptable refresh rate before finalising.
