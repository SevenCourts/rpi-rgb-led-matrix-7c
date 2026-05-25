# XL1 Layout — Final Decisions (Phase 1 Input)

This file consolidates user decisions on top of the agent-authored v1 specs in this directory. It is the **authoritative source** for Phase 1 implementation. Where it contradicts other files in this directory, this file wins.

## Architecture decisions

- **`PANEL_TYPE` env var** (current mechanism) stays. M1=192×64, L1=192×96, XL1=320×96.
- **`W_LOGO_WITH_CLOCK`** — per-panel-type constant in `dimens.py`. Values: M1=120 (unchanged), XL1=160.
- **`FONT_CLOCK_DEFAULT`** — exported from `dimens.py` alongside `W_PANEL`/`H_PANEL`. Values: M1=`FONT_XL_SDK` (texgyre-27, unchanged), XL1=`FONT_XL_7SEGMENT` (44px glyph) by default; `FONT_XXL_7SEGMENT` selectable for headline clock.
- **`pick_font_that_fits()`** — refactored to accept a candidate font list as a parameter. Callers pass per-panel-type lists. M1 default `[FONT_L, FONT_M, FONT_S]` (unchanged). XL1 default `[FONT_XL, FONT_L, FONT_M, FONT_S]`.
- **Upload-time image scaling** — backend behavior unknown; investigation deferred. Firmware should be defensive: assume images may be any size and scale to fit on render. Tracked as an open question for the backend repo.

## Scoreboard v1 — override of scoreboard.md

The agent's v1 spec proposes a 50/50 split at x=160. **Replace** with a content-sized score zone:

### Score zone — content-sized
- Score zone width ≈ **150 px**, starts at **x=170**.
- Layout within score zone (left to right):
  - Set columns: 3 × 22 px = 66 px in `FONT_L_SPLEEN` (x=170..235)
  - Gap + service indicator + gap: ~14 px (x=236..249)
  - Game score: 2-digit `FONT_XL_7SEGMENT` (advance **32 px** per char measured from BDF → 64 px), right-aligned to x=316 (x=253..316)
  - Right margin: 3 px (x=317..319)
- Name zone: x=0..169 (170 px wide).
- **No slack for a 4th set column** at this font choice — adequate for tennis but worth noting.
- **`'1'` glyph in FONT_XL_7SEGMENT** is right-aligned within its 32 px slot (authentic 7-segment style). Ship as-is — matches real LED scoreboards.

### Doubles name truncation
- `MAX_LENGTH_NAME_DOUBLES` for XL1: **8 chars** (vs M1's 3).
- Singles font: FONT_XL (spleen-16×32), name available width = 170 − 27 (flag) − 2 (gap) − 3 (margin) = **138 px** → ~8 chars at FONT_XL.

### Flags
- v1: **27×18 px**, runtime-scaled from existing 18×12 source images using PIL nearest-neighbor. New constants `W_FLAG_XL1=27`, `H_FLAG_XL1=18` in `dimens.py`.
- **v2 requirement (not optional)**: hand-drawn pixel-perfect flag images at the XL1 target size. PIL scaling is acceptable for the initial release only.

## Design principles (durable rules)

These rules apply to all current and future panel form factors, including L1 and any successor:

1. **Score zone is content-sized, name zone takes the rest.** Score zone width = sum of (3 set columns + service indicator + game score) plus minimal padding. Do not size the score zone as a fixed fraction of panel width.
2. **Flag images must be pixel-perfect, not PIL-scaled, in production-mature releases.** Runtime scaling is acceptable for v1 of a new panel type only.

## Fonts — not locked to current set

The agent's v1 specs choose fonts from the existing BDF set in `rgbmatrix.py` (Spleen 5×8 through 32×64, texgyre-27, 7-segment 26/45/66, tom-thumb). **For XL1 we are explicitly free to introduce additional fonts** — bigger or differently-styled — if the existing set proves suboptimal for the larger panel.

Candidate sources when adding fonts:
- Larger 7-segment variants (custom BDF generated from TTF, e.g. via `otf2bdf` from a 7-segment TTF) for clock and game scores above 66 px.
- Wider/heavier sans BDFs for high-contrast names at distance — Spleen tops out at 32×64; bigger heavyweight options exist (e.g. `unifont`-derivatives, custom-generated from Inter or similar).
- Custom pixel fonts hand-drawn for SevenCourts brand consistency.

Acceptance criterion: any new font ships as a BDF file under the same loading path as existing fonts (`load_font()` in `rgbmatrix.py`). New fonts get an alias constant (`FONT_XL1_HEADLINE`, etc.) so per-panel-type Layout objects can reference them by name.

Decision deferred until Phase 2 (XL1 implementation on hardware) — the existing fonts may be sufficient. If not, font additions are a normal extension, not a rewrite.

## Open questions deferred to later phases

- Backend upload-scaling behavior — investigate in the backend repo before image rendering becomes a problem on XL1 in production.
- v2 layout selection: which v2 proposal(s) (clock+weather, message+QR, feature-match signage, etc.) get prioritized after v1 ships.
- Whether to introduce new BDF fonts for XL1 — defer to Phase 2 hardware-bench review.
- **Signage cell name truncation** (`MAX_LENGTH_NAME_SINGLES_XL1`) — mockup geometry supports 12 chars at FONT_S_SPLEEN; spec proposed 15. Ship Phase 2 with 12 chars; revisit on hardware bench. If players complain, shrink score zone by ~18 px to recover room for 15-char names.
- XL1-native logo content — current preset logos are M1-sized (192×64) and look blocky when nearest-neighbor scaled into XL1's logo zone. Separate content-side task; firmware just renders what it's given.
