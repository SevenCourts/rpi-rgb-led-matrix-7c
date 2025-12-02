from sevencourts.rgbmatrix import *
from sevencourts.m1.dimens import *

FONT_CLOCK_S_1 = FONT_L_7SEGMENT
FONT_CLOCK_M_1 = FONT_XL_7SEGMENT
FONT_CLOCK_L_1 = FONT_XXL_7SEGMENT
FONT_CLOCK_S_2 = FONT_L_SPLEEN
FONT_CLOCK_M_2 = FONT_XL_SPLEEN
FONT_CLOCK_L_2 = FONT_XXL_SPLEEN
W_LOGO_WITH_CLOCK = 120  # left from clock


def draw_clock_by_coordinates(
    cnv, time_now, x, y, font, color=COLOR_CLOCK_DEFAULT, time_preset=None
):
    if time_preset:
        time_now = time_preset.strftime("%H:%M")
    draw_text(cnv, x, y, time_now, font, color)


def draw_clock(cnv, time_now, clock, color=COLOR_CLOCK_DEFAULT):
    if clock == None:
        # display a clock using the default font and coordinates
        font = FONT_CLOCK_DEFAULT
        x = W_LOGO_WITH_CLOCK
        y = 62
    elif clock:
        clock_size = clock.get("size")
        clock_font = clock.get("font")
        clock_h_align = clock.get("h-align")
        clock_v_align = clock.get("v-align")

        if clock_font == "font-2":
            if clock_size == "small":
                font = FONT_CLOCK_S_2
            elif clock_size == "medium":
                font = FONT_CLOCK_M_2
            else:
                font = FONT_CLOCK_L_2
        else:
            if clock_size == "small":
                font = FONT_CLOCK_S_1
            elif clock_size == "medium":
                font = FONT_CLOCK_M_1
            else:
                font = FONT_CLOCK_L_1

        if clock_h_align == "left":
            x = 0
        elif clock_h_align == "center":
            x = max(1, (W_PANEL - width_in_pixels(font, time_now)) / 2)
        else:
            x = max(0, W_PANEL - width_in_pixels(font, time_now))

        if clock_v_align == "top":
            y = y_font_offset(font)
        elif clock_v_align == "center":
            y = (H_PANEL + y_font_offset(font)) / 2
        else:
            y = H_PANEL
    else:
        return
    draw_clock_by_coordinates(cnv, time_now, x, y, font, color)
