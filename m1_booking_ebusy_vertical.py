from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import gettext
import m1_clock
import m1_image
from m1_booking_utils import *

# fonts
f_clock = FONT_M_SDK
f_booking_info_pri = FONT_XS
f_booking_info_sec = FONT_XXS
f_booking_court = FONT_M

# colors
## TABB
c_CI_pri = graphics.Color(5, 105, 167) # blue
c_CI_sec = COLOR_WHITE # white

c_grid = None # COLOR_7C_GOLD

c_clock = COLOR_WHITE
c_clock_separator = COLOR_GREY_DARK
c_booking_court = c_CI_sec
c_booking_court_bg = c_CI_pri
c_booking_info_sec = COLOR_GREY
c_booking_info_pri = COLOR_WHITE
c_booking_info_sec_free = COLOR_GREEN

def _booking_line_heights(courts_count:int = 3):
    '''Returns a tuple of integers, indicating heights of the lines or None:
    (total, row_sec, row_pri_1, row_pri_2)
    '''
    switcher = {
        2: (int(H_PANEL / 2), 8, 12, 12),   # 32
        3: (int(H_PANEL / 3), 5, 7, 7),     # 21
        4: (int(H_PANEL / 4), 6, 10, None), # 16
    }
    return switcher.get(courts_count, int(H_PANEL / 3))

def draw(cnv, booking_info, panel_tz):

    total_courts = len(booking_info['courts'])

    # heights and widths
    w_clock = w_logo = width_in_pixels(f_clock, "00:00")
    h_clock = y_font_offset(f_clock) + 1
    h_logo = H_PANEL - h_clock

    line_heights = _booking_line_heights(total_courts)
    
    w_booking = W_PANEL - max(w_clock, w_logo)

    # x, y coordinates
    x_clock = x_logo = W_PANEL - w_clock
    y_logo = 0
    y_clock = H_PANEL - h_clock
        
    # render
    ## background fills
    ### court names bg
    
    ### logo placeholder bg
    #fill_rect(cnv, x_logo, y_logo, w_logo, h_logo, c_CI_primary)

    if c_grid:
        ### vertical line separating clock
        graphics.DrawLine(cnv, x_clock, 0, x_clock, H_PANEL, c_grid)
        ### horizontal line separating clock and logo
        graphics.DrawLine(cnv, x_clock, y_clock, W_PANEL, y_clock, c_grid)

    # vertical line separating clock
    x = x_clock - 1
    graphics.DrawLine(cnv, x, 0, x, H_PANEL, c_clock_separator)
    
    ## clock
    m1_clock.draw_clock_by_coordinates(cnv, x_clock, y_clock + h_clock - 1, f_clock, panel_tz, c_clock)

    ## logo
    logo_img = Image.open('images/logos/TABB/tabb-logo-transparent-60x13.png')
    m1_image.thumbnail(logo_img, w_logo, h_logo)
    h_logo_img = logo_img.height
    w_logo_img = logo_img.width    
    x_logo_img = x_logo
    y_logo_img = y_logo + int((h_logo - h_logo_img)/2)
    cnv.SetImage(logo_img.convert('RGB'), x_logo_img, y_logo_img)
    round_rect_corners(cnv, x_logo_img, y_logo_img, logo_img.width, logo_img.height)

    ## booking infos
    y = 0
    for b in booking_info['courts']:
        _draw_booking_court(cnv, 0, y, line_heights, w_booking, b)
        y += line_heights[0]

def _draw_booking_court(cnv, x0: int, y0:int, line_heights, w:int, court_bookings):

    court_name = court_bookings['court']['name']

    (h_total, h_row_sec, h_row_pri_1, h_row_pri_2) = line_heights    
    w_court_name = 25

    max_length_court_name = 3

    # court name
    txt = court_name[:max_length_court_name]
    fnt = f_booking_court
    x = x0
    y = y0 + 1
    _w = w_court_name
    _h = h_total - 2
    fill_rect(cnv, x, y, _w, _h, c_booking_court_bg, round_corners=True)        
    x += x_font_center(txt, _w+2, fnt)
    y += y_font_center(fnt, _h)
    graphics.DrawText(cnv, fnt, x, y, c_booking_court, txt)

    # Booking info (up to 3 rows)
    info_sec = info_pri_1 = info_pri_2 = ''
    
    current = court_bookings['current']
    if current:
        
        info_sec = ">>> 6 min." # FIXME
        c_sec = c_booking_info_sec

        txt = current['display-text']
        if txt:
            w_info = w - w_court_name
            if h_row_pri_2:            
                MAX_ROW_LENGTH = max_string_length_for_font(f_booking_info_pri, w_info)
                for wrd in txt.split():
                    if info_pri_1:
                        if len(info_pri_1 + ' ' + wrd) <= MAX_ROW_LENGTH:
                            info_pri_1 = info_pri_1 + ' ' + wrd
                        else:
                            info_pri_2 = info_pri_2 + (' ' if info_pri_2 else '') + wrd
                    else:
                        info_pri_1 = wrd
                if len(info_pri_2) > MAX_ROW_LENGTH:
                    # ellipsize 2nd row            
                    info_pri_2 = info_pri_2[:MAX_ROW_LENGTH]
            else:
                info_pri_1 = truncate_text(f_booking_info_pri, w_info, txt)
        else:
            info_pri_1 = booking_team(current, True)
            info_pri_2 = booking_team(current, False)            
    else:
        c_sec = c_booking_info_sec_free
        info_sec = "Free to book"
    
    # secondary info
    x = x0 + w_court_name + 2
    if info_pri_1:
        y = y0 + 1 + h_row_sec
    else:
        y = y0 + (h_total + y_font_offset(f_booking_info_sec) ) / 2
    graphics.DrawText(cnv, f_booking_info_sec, x, y, c_sec, info_sec)
    
    # primary info
    if info_pri_1:
        c = c_booking_info_pri
        if info_pri_2:
            y += h_row_pri_1
            graphics.DrawText(cnv, f_booking_info_pri, x, y, c, info_pri_1)
            y += h_row_pri_2            
            graphics.DrawText(cnv, f_booking_info_pri, x, y, c, info_pri_2)
        else:
            y += h_row_pri_1 + (h_row_pri_2 / 2)
            graphics.DrawText(cnv, f_booking_info_pri, x, y, c, info_pri_1)

    if c_grid:
        ### vertical line separating booking court from info
        graphics.DrawLine(cnv, w_court_name, 0, w_court_name, H_PANEL, c_grid)
        ### horizontal line between bookings
        graphics.DrawLine(cnv, x0, y0 + h_total, x0 + w, y0 + h_total, c_grid)

    return