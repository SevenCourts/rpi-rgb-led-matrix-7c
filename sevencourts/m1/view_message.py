from sevencourts.m1.dimens import *
from sevencourts.rgbmatrix import *
from sevencourts.m1.layouts import current_layout
import sevencourts.m1.view_clock as v_clock


def draw(canvas, idle_info, time_now):
    layout = current_layout().message
    message = idle_info.get("message", "")
    h_available = _message_zone_height(layout)
    w_available = W_PANEL

    lines = message.split("\n")
    candidates = layout.font_candidates or None

    if len(lines) == 1:
        l0 = lines[0]
        font = pick_font_that_fits(w_available, h_available, l0, candidates=candidates)
        x0 = max(0, (w_available - width_in_pixels(font, l0)) / 2)
        y0 = y_font_center(font, h_available)
        graphics.DrawText(canvas, font, x0, y0, layout.color_message, l0)
    else:
        l0 = lines[0]
        l1 = lines[1]
        font = pick_font_that_fits(
            w_available, h_available, l0, l1, candidates=candidates
        )

        x0 = max(0, (w_available - width_in_pixels(font, l0)) // 2)
        y0 = y_font_center(font, h_available // 2)
        graphics.DrawText(canvas, font, x0, y0, layout.color_message, l0)

        x1 = max(0, (w_available - width_in_pixels(font, l1)) // 2)
        y1 = y0 + y_font_center(font, h_available // 2)
        graphics.DrawText(canvas, font, x1, y1, layout.color_message, l1)

    if idle_info.get("clock") is True:
        _draw_clock(canvas, layout, time_now)


def _message_zone_height(layout) -> int:
    """Height available for the message text, reserving room for the clock strip."""
    if layout.clock_divider_y is not None:
        return layout.clock_divider_y
    # Legacy M1 behavior: reserve a fixed clock strip at the bottom.
    return H_PANEL - 2 - 20 - 2


def _draw_clock(canvas, layout, time_now):
    """Draw the clock under the message. M1 uses legacy `draw_clock(..., None)`;
    panels that customise clock placement (e.g. XL1) supply explicit Layout fields.
    """
    if layout.clock_divider_y is not None:
        fill_rect(
            canvas, 0, layout.clock_divider_y, W_PANEL, 1, layout.color_clock_divider
        )

    font = layout.clock_font
    if font is None:
        v_clock.draw_clock(canvas, time_now, None)
        return

    text = time_now if time_now is not None else "--:--"
    if layout.clock_right_aligned:
        # 4px right margin matches the XL1 mockup.
        x = W_PANEL - width_in_pixels(font, text) - 4
    else:
        x = layout.clock_x
    draw_text(canvas, x, layout.clock_y, text, font, layout.clock_color)
