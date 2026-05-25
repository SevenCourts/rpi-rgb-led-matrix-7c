from sevencourts.rgbmatrix import *
from sevencourts.m1.dimens import *
from sevencourts.m1.layouts import current_layout


def draw_clock_by_coordinates(
    cnv, time_now, x, y, font, color=COLOR_CLOCK_DEFAULT, time_preset=None
):
    if time_now is None:
        time_now = "--:--"

    if time_preset:
        time_now = time_preset.strftime("%H:%M")

    draw_text(cnv, x, y, time_now, font, color)


def draw_clock(cnv, time_now, clock, color=COLOR_CLOCK_DEFAULT):
    layout = current_layout().clock
    if time_now is None:
        time_now = "--:--"
    if clock is None:
        font = FONT_CLOCK_DEFAULT
        x = W_LOGO_WITH_CLOCK
        y = H_PANEL - 2
    elif clock:
        # `clock: true` is the legacy "default config" sentinel; treat as empty dict.
        cfg = clock if isinstance(clock, dict) else {}
        font = _pick_font(layout, cfg)
        x = _pick_x(font, time_now, cfg.get("h-align"))
        y = _pick_y(font, cfg.get("v-align"))
    else:
        return
    draw_clock_by_coordinates(cnv, time_now, x, y, font, color)


def _pick_font(layout, clock):
    size = clock.get("size")
    if clock.get("font") == "font-2":
        if size == "small":
            return layout.font_clock_s_2
        if size == "medium":
            return layout.font_clock_m_2
        return layout.font_clock_l_2
    if size == "small":
        return layout.font_clock_s_1
    if size == "medium":
        return layout.font_clock_m_1
    return layout.font_clock_l_1


def _pick_x(font, time_now, h_align):
    if h_align == "left":
        return 0
    if h_align == "center":
        return max(1, (W_PANEL - width_in_pixels(font, time_now)) / 2)
    return max(0, W_PANEL - width_in_pixels(font, time_now))


def _pick_y(font, v_align):
    if v_align == "top":
        return y_font_offset(font)
    if v_align == "center":
        return (H_PANEL + y_font_offset(font)) / 2
    return H_PANEL
