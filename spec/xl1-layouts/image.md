# XL1 Image Layout

Idle mode: a promotional or preset image fills the panel, optionally with a clock alongside it.

**Viewing mode:** Public, 7m+. Image must fill the canvas purposefully; clock (if shown) must be legible.  
**M1 reference:** `sevencourts/m1/view_image.py`

---

## M1 Baseline (for reference)

On M1 (192×64):
- If clock is requested (`idle_info.get("clock") == True`) AND the image is narrow enough to fit alongside (image.width < W_LOGO_WITH_CLOCK = 120):
  - Image scaled to fit within 120×64, centered in left zone.
  - Clock drawn at x=120, y=62 (H_PANEL - 2) using `FONT_CLOCK_DEFAULT = FONT_XL_SDK`.
- Otherwise: image scaled to fill full 192×64, centered.
- Scaling via `imgs.scale_to_fit(image, max_width, H_PANEL)` — maintains aspect ratio, no upscaling beyond natural size.
- Uploaded images are scaled to full panel height on upload (as per recent change in startup log).

The `_can_show_clock(image)` check: returns True only if image.width < 120 after scaling. This means portrait-format images show the clock; landscape images fill the panel and hide the clock.

---

## Section 1: v1 — Same Elements, Bigger Canvas

### Design Principle

The image view is nearly self-scaling: `scale_to_fit()` uses `W_PANEL` and `H_PANEL` from dimens.py dynamically, and `canvas.SetImage()` places at computed (x, y). The main v1 changes are:

1. Update `W_LOGO_WITH_CLOCK` for XL1 — affects how the logo+clock layout works.
2. The clock font in the logo+clock layout should upgrade to match the larger panel.
3. The `_can_show_clock()` threshold is currently `image.width < 120`. On XL1 this threshold should be `image.width < W_LOGO_WITH_CLOCK` (already the case in code) — just ensure `W_LOGO_WITH_CLOCK` is set correctly for XL1.

### Zone Map

**Variant A: Full-panel image (no clock, or image too wide for side-by-side)**

```
x=0                                  x=319
+--------------------------------------+  y=0
|                                      |
|       IMAGE (scaled to fit 320×96)   |
|       Centered with black fill       |
|                                      |
+--------------------------------------+  y=95
```

- `scale_to_fit(image, 320, 96)` — scales image to fit 320×96, maintaining aspect ratio.
- x = (320 - image.width) // 2
- y = (96 - image.height) // 2
- Remaining pixels: `COLOR_BLACK` (canvas is cleared to black before draw).

**Variant B: Logo (left) + Clock (right)**

```
x=0          x=159  x=160              x=319
+-------------+------+------------------+  y=0
|             |      |                  |
|    IMAGE    |      |    HH:MM         |
|  (≤160×96) |      | (FONT_XL_7SEG)  |
|             |      |                  |
+-------------+------+------------------+  y=95
```

- Logo zone: x=0..159, height=96.
- Clock zone: x=160..319, height=96.
- `W_LOGO_WITH_CLOCK = 160` for XL1.
- Clock: `FONT_XL_7SEGMENT` (44px glyph, ~28px per char). "HH:MM" = 5×28 = 140px.
  - x = 160 + (160 - 140) // 2 = **170**.
  - y = `y_font_center(FONT_XL_7SEGMENT, 96)` = (96-44)//2 + 44 = **70**.
- `_can_show_clock(image)` condition: `image.width < 160` (after scaling to fit the logo zone).

### Pixel Budget

| Element | x | y | w | h |
|---------|---|---|---|---|
| Image (full panel) | (320-img.w)//2 | (96-img.h)//2 | img.w | img.h |
| Image (logo zone) | (160-img.w)//2 | (96-img.h)//2 | img.w | img.h |
| Clock text | 170 | 70 (baseline) | 140 | 44 |

No overflow possible — all placements are computed dynamically from panel dimensions.

### Image Scaling Notes

- `scale_to_fit()` in `sevencourts/images.py` maintains aspect ratio and does not upscale. For XL1, uploaded images should ideally be 320×96 native, but 192×64 images will still render (centered with black borders).
- Preset images in `images/logos/` are fixed-size PNGs. They will be centered in the available zone. Logos designed for M1's 192×64 will appear surrounded by black on XL1's 320×96. This is acceptable in v1 but warrants uploading XL1-specific logos (see v2 proposals).
- The upload scaling behavior (recent change: "Scale uploaded images to full panel height") — on XL1 this means uploads are scaled to 96px height. Backend or client-side upload path needs to know the panel type to scale correctly. **Open question: does the upload endpoint know the panel type? Is scaling done server-side or client-side?**

### Rationale

- The image view is almost entirely driven by `W_PANEL`, `H_PANEL`, and `W_LOGO_WITH_CLOCK` constants. The primary v1 task is setting `W_LOGO_WITH_CLOCK = 160` for XL1 and upgrading the clock font in the adjacent-clock path.
- Keeping `W_LOGO_WITH_CLOCK = W_PANEL // 2` as a formula in dimens.py is the cleanest approach and removes the one hardcoded constant in view_clock.py.

### Open Questions

1. **Upload scaling**: Images are scaled to full panel height on upload. Does the upload path know it's targeting XL1 (96px) vs M1 (64px)? If scaling happens at upload time server-side, this needs a panel-type parameter.
2. **Preset logo files**: `images/logos/` contains M1-sized images. Should XL1-sized versions be added, or should the image loader detect and auto-scale?
3. **`W_LOGO_WITH_CLOCK`**: Should this be exactly `W_PANEL // 2 = 160` (symmetric split) or tuned to image aspect ratios? A SevenCourts logo at standard 16:9 ratio would be 170×96 — wider than 160px, which would disable the clock. Something like `W_PANEL * 0.45 = 144` might be more practical.

---

## Section 2: v2 Proposals

### Proposal A: Image + Metadata Overlay Strip

**Concept:** Show the full-panel image (320×96) but overlay a semi-transparent (approximated with dimmed pixels) bottom strip showing the image caption or event name.

Since the LED panel has no alpha compositing, the "overlay" is a filled rectangle over the bottom of the image with a dimmed but non-black background. Text sits on top.

```
+----------------------------------------+
|                                        |  y=0..79
|         IMAGE (320×80)                 |
|                                        |
+========================================+  y=80 (1px separator)
|  SAARLAND OPEN 2026  •  Court 3        |  y=81..95 (text strip, dark fill)
+----------------------------------------+
```

- Image: scaled to fit 320×80 (not full 96px — 16px reserved for strip).
- Strip: y=80..95, fill with `COLOR_7C_DARK_BLUE` (37,56,73).
- Caption text: `FONT_S` (spleen-6x12, 8px glyph). Max ~53 chars at 320px — plenty.
  - "SAARLAND OPEN 2026  •  Court 3" = 31 chars × 6px = 186px. x-centered = (320-186)//2 = **67**. y=**91** (baseline).
  - Color: `COLOR_WHITE`.
- Separator: 1px at y=80, `COLOR_7C_GOLD`.

**Pros:** Contextualizes the promotional image — makes a sponsor logo or tournament banner self-describing. The strip uses space that would otherwise be black (images rarely exactly fill 320×96). The colored strip provides visual closure at the bottom.  
**Cons:** The idle_info schema would need a `caption` field alongside `image-url`. Currently `idle_info` has only `image-url` and optional `clock`. Minor implementation cost.  
**Backend data needed:** `caption` string field in `idle_info`.

---

### Proposal B: Dual Image (Portrait × 2)

**Concept:** Side-by-side display of two portrait-format images (each 160×96), allowing two sponsors or two team logos to be shown simultaneously.

```
+--------------------+--------------------+
|                    |                    |
|   IMAGE 1          |   IMAGE 2          |
|   (160×96)        |   (160×96)         |
|                    |                    |
+--------------------+--------------------+
```

- Image 1: scaled to fit 160×96, centered at x=0..159.
- Image 2: scaled to fit 160×96, centered at x=160..319.
- Separator: 1px vertical line at x=159, `COLOR_7C_DARK_GREY`.
- Clock: omitted in this layout (no room without reducing image zones).

**Pros:** Dramatically more useful for tournament panels that need to show two sponsors, or for a "today's featured match" layout with two player headshots. The 320px width is purpose-built for this — two M1-width panels side by side.  
**Cons:** Requires two separate image URLs in the idle_info — a new schema field (`image-url-2`). If only one image is provided, falls back to single full-panel layout. Portrait format is the assumed shape — landscape images would need creative cropping or letter-boxing.  
**Backend data needed:** `image-url-2` field in `idle_info`.

---

### Proposal C: Image Carousel (2 images, alternating every N seconds)

**Concept:** Keep the same single-image layout but rotate between two images every 30 seconds. The render loop already redraws on state change — if the server sends alternating panel states (or the client cycles locally), this works without architectural changes.

Simplest implementation: client-side rotation. Add an `image-urls` list field to idle_info. The view picks `image-urls[int(time_now.second / 30) % len(image_urls)]` for the current image. This is stateless and consistent across panel restarts.

```
+----------------------------------------+
|                                        |
|   IMAGE (320×96, rotating every 30s)  |
|                                        |
|                                        |
+----------------------------------------+
  [0s–30s: sponsor A]   [30s–60s: sponsor B]
```

**Pros:** Zero infrastructure cost if done client-side. Two sponsors get equal panel time. No additional server polling.  
**Cons:** Client-side rotation means the server has no control over timing. If the panel reboots mid-cycle, both sponsors see slightly unequal time. A cleaner approach routes through the server, but that adds polling complexity. Also: the LED matrix render loop only redraws on state change — a client-side time-based image swap would need to artificially trigger state changes (e.g. by advancing a counter in PanelState each second).  
**Backend data needed:** `image-urls` list field in `idle_info` (or handled purely client-side with existing `image-url` if server rotates it).
