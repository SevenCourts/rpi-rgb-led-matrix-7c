from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import gettext
import requests
import m1_clock
import m1_image

logger = m1_logging.logger("eBusy")

# Style sheet
FONT_COURT_NAME = FONT_S
FONT_CURRENT_TIME = FONT_S
FONT_TIME_BOX = FONT_M
FONT_BOOKING_CAPTION = FONT_S
FONT_BOOKING_NAME = FONT_M
FONT_MESSAGE = FONT_M

COLOR_HEADER_BG = COLOR_SV1845_2

COLOR_COURT_NAME = COLOR_WHITE
COLOR_CURRENT_TIME = COLOR_WHITE

COLOR_TIME_BOX = COLOR_WHITE
COLOR_TIME_BOX_BG_INFO = COLOR_SV1845_2
COLOR_TIME_BOX_BG_WARN = COLOR_SV1845_1

COLOR_BOOKING = COLOR_WHITE
COLOR_MESSAGE = COLOR_YELLOW

COLOR_SEPARATOR_LINE = COLOR_SV1845_1

MARGIN = 2
H_HEADER = 12

TD_0_UPCOMING = timedelta(minutes = -5)
TD_1_WELCOME = timedelta(minutes = 2)
TD_3_COUNTDOWN = timedelta(minutes = -5)
TD_4_GAMEOVER = timedelta(minutes = 2)

court_1 = {
            'court': {'id': 1, 'name': 'BBG Court'},
            'past': None,
            'current': {
                'start-date': '2025-07-17T13:30:00+04:00',
                'end-date': '2025-07-17T14:00:00+04:00', 
                'display-text': 'Verbandspiel H1 gg. TC Rechberghausen-Birenbach', 
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'}, 'p2': None, 'p3': None, 'p4': None},
            'next': {
                'start-date': '2025-07-17T14:00:00+04:00',
                'end-date': '2025-07-17T14:30:00+04:00', 
                'display-text': '', 
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'}, 
                'p2': {'firstname': 'Roman', 'lastname': 'Churkov'}, 
                'p3': None, 'p4': None}}

court_2 = {
            'court': {'id': 2, 'name': 'CUPRA Court präsentiert von Casa Automobile'},
            'past': None,
            'current': None,
            'next': None}

court_3 = {
            'court': {'id': 3, 'name': 'EKW'},
            'past': None,
            'current': None,
            'next': None}

booking_3_courts = {
    '_dev_timestamp': '2025-07-17T13:58:16+04:00',
    'courts': (court_1, court_2, court_3)}

# fonts
f_clock = FONT_M_SDK
f_booking_info_pri = FONT_XS
f_booking_info_sec = FONT_XXS
f_booking_court = FONT_M

# colors
c_CI_primary = graphics.Color(5, 105, 167) # TABB blue
c_CI_secondary = COLOR_7C_GOLD # COLOR_WHITE # TABB white

c_grid = None # COLOR_7C_GOLD

c_clock = COLOR_WHITE
c_booking_court = COLOR_WHITE
c_booking_info_text = COLOR_WHITE
c_booking_info_header = c_CI_primary
c_booking_info_header_free = COLOR_GREEN
c_booking_info_header_warning = COLOR_7C_GOLD

def _booking_line_height(courts_count:int = 3):
    switcher = {
        2: int(H_PANEL / 2), # 32
        3: int(H_PANEL / 3), # 21
        4: int(H_PANEL / 4), # 16
    }
    return switcher.get(courts_count, int(H_PANEL / 3))

def draw(cnv, booking_info, panel_tz):

    courts_count = 3

    # heights and widths
    w_clock = w_logo = 60
    h_clock = 16
    h_logo = H_PANEL - h_clock

    h_booking = _booking_line_height(courts_count)
    w_booking = W_PANEL - max(w_clock, w_logo)

    # x, y coordinates
    x_clock = x_logo = W_PANEL - w_clock
    y_logo = 0
    y_clock = H_PANEL - h_clock
    x_booking = 0
    y_booking_1 = 0
    y_booking_2 = y_booking_1 + h_booking
    y_booking_3 = y_booking_2 + h_booking

    # court names (3 letters only)
    
    y_booking_court_1 = y_font_center(f_booking_court, h_booking)
    y_booking_court_2 = y_booking_court_1 + h_booking
    y_booking_court_3 = y_booking_court_2 + h_booking

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

    ## clock
    x_clock_text = x_clock + x_font_center("21:55", w_clock, f_clock)
    y_clock_text = y_clock + y_font_center(f_clock, h_clock)
    m1_clock.draw_clock_by_coordinates(cnv, x_clock_text, y_clock_text, f_clock, panel_tz, c_clock)

    ## logo
    logo_img = Image.open('images/logos/TABB/tabb-logo-transparent-60x13.png')
    m1_image.thumbnail(logo_img, w_logo, h_logo)
    h_logo_img = logo_img.height
    w_logo_img = logo_img.width    
    x_logo_img = x_logo
    y_logo_img = y_logo + int((h_logo - h_logo_img)/2)
    cnv.SetImage(logo_img.convert('RGB'), x_logo_img, y_logo_img)
    round_rect_corners(cnv, x_logo_img, y_logo_img, logo_img.width, logo_img.height)

    ## booking info    
    _draw_booking_court(cnv, 0, y_booking_1, h_booking, w_booking, 
                        "CUPRA Court präsentiert von Casa Automobile", "Ilya, Roman, Alexander, Mario", "Time left: 15 min.")
    _draw_booking_court(cnv, 0, y_booking_2, h_booking, w_booking, "BBG court")
    _draw_booking_court(cnv, 0, y_booking_3, h_booking, w_booking, "EKW", "Herren 1", "Training")

def _draw_booking_court(cnv, x0: int, y0:int, h:int, w:int, court_name='-', info_pri=None, info_sec=''):

# c_booking_free
    w_court_name = 36
    max_length_court_name = 3

    # court name
    txt = court_name[:max_length_court_name]
    fnt = f_booking_court
    margin = 2
    x = x0 + margin
    y = y0 + margin
    _w = w_court_name - margin - 1
    _h = h - margin - 1
    fill_rect(cnv, x, y, _w, _h, c_CI_primary, round_corners=True)        
    x += x_font_center(txt, _w, fnt)
    y += y_font_center(fnt, _h)
    graphics.DrawText(cnv, fnt, x, y, c_booking_court, txt)
    
    # secondary info
    margin = 3
    x = x0 + w_court_name + 1
    y = y0 + margin + y_font_offset(f_booking_info_sec)
    if info_pri:        
        w_info = w - w_court_name
        txt = truncate_text(f_booking_info_sec, w_info, info_sec)
        c = c_booking_info_header_warning if "Time left" in txt else c_booking_info_header        
        graphics.DrawText(cnv, f_booking_info_sec, x, y, c, txt)
        # primary info
        txt = truncate_text(f_booking_info_pri, w_info, info_pri)
        c = c_booking_info_text
        y += margin + y_font_offset(f_booking_info_pri)
        graphics.DrawText(cnv, f_booking_info_pri, x, y, c, txt)
    else:
        txt = 'Free to book'
        graphics.DrawText(cnv, f_booking_info_sec, x, y, c_booking_info_header_free, txt)

    if c_grid:
        ### vertical line separating booking court from info
        graphics.DrawLine(cnv, w_court_name, 0, w_court_name, H_PANEL, c_grid)
        ### horizontal line between bookings
        graphics.DrawLine(cnv, x0, y0 + h, x0 + w, y0 + h, c_grid)

    return