import os
from sevencourts import *

from datetime import datetime
from dateutil import tz

# Style constants
# Style sheet
## Clock styles
if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    FONT_CLOCK = FONT_L
else:
    FONT_CLOCK = FONT_XL_SDK
FONT_CLOCK_S_1=FONT_L_7SEGMENT
FONT_CLOCK_M_1=FONT_XL_7SEGMENT
FONT_CLOCK_L_1=FONT_XXL_7SEGMENT
FONT_CLOCK_S_2=FONT_L_SPLEEN
FONT_CLOCK_M_2=FONT_XL_SPLEEN
FONT_CLOCK_L_2=FONT_XXL_SPLEEN
COLOR_CLOCK = COLOR_WHITE
W_LOGO_WITH_CLOCK = 120 # left from clock


def draw_clock(canvas, clock, panel_tz, color=COLOR_CLOCK):

    dt = datetime.now(tz.gettz(panel_tz))
    text = dt.strftime('%H:%M')        

    if clock == True: # Compiler warning is WRONG!
        # display a clock along with some other elements, using the default Spleen font
        font = FONT_CLOCK
        x = W_LOGO_WITH_CLOCK
        y = 62
    elif clock:
        clock_size = clock.get('size')
        clock_font = clock.get('font')
        clock_h_align = clock.get('h-align')
        clock_v_align = clock.get('v-align')

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
            x = max(1, (W_PANEL - width_in_pixels(font, text)) / 2)
        else:
            x = max(0, W_PANEL - width_in_pixels(font, text))

        if clock_v_align == "top":
            y = y_font_offset(font)
        elif clock_v_align == "center":
            y = (H_PANEL + y_font_offset(font)) / 2
        else:
            y = H_PANEL
    else:
        return
    draw_text(canvas, x, y, text, font, color)
