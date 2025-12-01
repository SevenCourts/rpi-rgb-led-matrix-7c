from sevencourts.m1.dimens import *
from sevencourts.rgbmatrix import *
import sevencourts.m1.view_clock as v_clock

COLOR_MESSAGE = COLOR_7C_BLUE


def draw(canvas, idle_info, time_now):
    message = idle_info.get("message", "")
    h_available = H_PANEL - 2 - 20 - 2  # minus clock
    w_available = W_PANEL

    lines = message.split("\n")

    if len(lines) == 1:
        l0 = lines[0]
        font = pick_font_that_fits(w_available, h_available, l0)
        x0 = max(0, (w_available - width_in_pixels(font, l0)) / 2)
        y0 = y_font_center(font, h_available)
        graphics.DrawText(canvas, font, x0, y0, COLOR_MESSAGE, l0)
    else:
        l0 = lines[0]
        l1 = lines[1]
        font = pick_font_that_fits(w_available, h_available, l0, l1)

        x0 = max(0, (w_available - width_in_pixels(font, l0)) // 2)
        y0 = y_font_center(font, h_available // 2)
        graphics.DrawText(canvas, font, x0, y0, COLOR_MESSAGE, l0)

        x1 = max(0, (w_available - width_in_pixels(font, l1)) // 2)
        y1 = y0 + y_font_center(font, h_available // 2)
        graphics.DrawText(canvas, font, x1, y1, COLOR_MESSAGE, l1)

    clock = idle_info.get("clock")
    if clock == True:
        v_clock.draw_clock(canvas, time_now, None)
