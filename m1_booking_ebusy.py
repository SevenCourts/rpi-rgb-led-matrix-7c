from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import requests
import gettext
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

def draw_booking(cnv, booking_info, panel_tz):
    
    court = booking_info.get('court')
    b_0_past = booking_info.get('past')
    b_1_current = booking_info.get('current')
    b_2_next = booking_info.get('next')
    
    
    # Use datetime set in the Panel Admin UI for easier testing/debugging:
    _dev_timestamp = booking_info.get('_dev_timestamp')
    if _dev_timestamp and len(_dev_timestamp):
        t = parser.parse(_dev_timestamp)
    else:
        t = datetime.now(tz.gettz(panel_tz))

    # do not show time if no booking to show (time will be displayed in the main area)
    show_time_in_header = b_0_past or b_1_current or b_2_next
    h_header = _draw_header(cnv, court, t if show_time_in_header else None)

    if b_0_past and not b_1_current:
        # Show "Game over" for 2 minutes only if there is no current booking
        t_0_4_gameover_end = (parser.parse(b_0_past['end-date']) + TD_4_GAMEOVER)
        if t < t_0_4_gameover_end:
            w_timebox = _draw_time_box(cnv, h_header, COLOR_TIME_BOX_BG_INFO, 'Game', 'over')
            x0 = w_timebox + MARGIN * 2
            _draw_booking_match(cnv, x0, h_header, b_0_past, 'Danke fürs Spielen!')

    elif b_1_current:
        
        t_start = parser.parse(b_1_current['start-date'])
        t_end = parser.parse(b_1_current['end-date'])

        t_0_upcoming_start = (t_start + TD_0_UPCOMING)        
        t_1_welcome_end = (t_start + TD_1_WELCOME)
        t_3_countdown_start = (t_end + TD_3_COUNTDOWN)
        
        if t > t_0_upcoming_start:
            # 1. time box
            if t < t_3_countdown_start:
                w_timebox = _draw_time_box(cnv, h_header, COLOR_TIME_BOX_BG_INFO, t_start.strftime('%H:%M'), "-", t_end.strftime('%H:%M'))
            elif t < t_end:
                minutes_left = (t_end - t).seconds // 60 % 60
                if minutes_left == 0:
                    w_timebox = _draw_time_box(cnv, h_header, COLOR_TIME_BOX_BG_WARN, 'Letzte', 'Minute')
                else:
                    w_timebox = _draw_time_box(cnv, h_header, COLOR_TIME_BOX_BG_WARN, f"{minutes_left} min")
            else:
                raise ValueError('should never happen with eBusy data')

            # 2. message area
            x0 = w_timebox + MARGIN * 2
            if t < t_1_welcome_end:                
                _draw_booking_match(cnv, x0, h_header, b_1_current, 'Viel Spaß!')
            elif t < t_3_countdown_start:
                _draw_booking_match(cnv, x0, h_header, b_1_current)
            elif t < t_end:
                # Adjacent bookings handling
                    #  0 - 14 show current
                    # 15 - 29 show next
                    # 30 - 44 show current
                    # 45 - 59 show next
                if b_2_next and (t.second >= 15 and t.second <= 29) or (t.second >= 45 and t.second <= 59):
                    _draw_booking_match(cnv, x0, h_header, b_2_next, 'Nächste Buchung')                    
                else:
                    _draw_booking_match(cnv, x0, h_header, b_1_current)
            else:
                raise ValueError('should never happen with eBusy data')

    elif b_2_next:
        t_start = parser.parse(b_2_next['start-date'])
        t_end = parser.parse(b_2_next['end-date'])
        w_timebox = _draw_time_box(cnv, h_header, COLOR_TIME_BOX_BG_INFO, t_start.strftime('%H:%M'), "-", t_end.strftime('%H:%M'))
        x0 = w_timebox + MARGIN * 2
        _draw_booking_match(cnv, x0, h_header, b_2_next, 'Nächste Buchung')

    else:
        # no bookings - show a default
        image = Image.open('images/logos/SV1845/sv1845_76x64_eBusy_demo_logo.png')
        MAX_IMAGE_WIDTH = 76 # so that 22:22 time fits
        h_logo = H_PANEL - h_header - MARGIN - MARGIN
        m1_image.thumbnail(image, MAX_IMAGE_WIDTH, h_logo)
        x = MARGIN
        y = h_header + MARGIN
        cnv.SetImage(image.convert('RGB'), x, y)
        round_rect_corners(cnv, x, y, image.width, image.height)

        text = t.strftime('%H:%M')
        fnt = m1_clock.FONT_CLOCK_M_1
        x = image.width + MARGIN + MARGIN
        x = x + x_font_center(text, W_PANEL - x, fnt)
        y = h_header + y_font_center(fnt, H_PANEL - h_header)
        draw_text(cnv, x, y, text, fnt, COLOR_CLOCK_DEFAULT)

def _draw_header(cnv, court, dt=None):
    """Retuns the y coordinate (height) of the header section"""        
    x_court_name = 0 + MARGIN
    y_court_name = y_font_offset(FONT_COURT_NAME) + MARGIN
    
    if dt:
        clock_str = dt.strftime('%H:%M') # FIXME WTF
        x_clock = W_PANEL - MARGIN - width_in_pixels(FONT_CURRENT_TIME, clock_str)    
        y_clock =  y_font_offset(FONT_CURRENT_TIME) + MARGIN        
        y_separator = max(y_clock, y_court_name) + MARGIN                
    else:
        y_separator = y_court_name + MARGIN

    fill_rect(cnv, 0, 0, W_PANEL, y_separator, COLOR_HEADER_BG)
    draw_text(cnv, x_court_name, y_court_name, court['name'], FONT_COURT_NAME, COLOR_COURT_NAME)
    if dt:
        draw_text(cnv, x_clock, y_clock, clock_str, FONT_CURRENT_TIME, COLOR_CURRENT_TIME)
    graphics.DrawLine(cnv, 0, y_separator, W_PANEL, y_separator, COLOR_SEPARATOR_LINE)

    return y_separator + 1

def _draw_time_box(cnv, y0, color_bg, txt_1:str, txt_2:str=None, txt_3:str=None):
    '''Return the width of the timebox component'''
    font = FONT_TIME_BOX
    padding = 1
    x = MARGIN
    y = y0 + MARGIN
    h = H_PANEL - y0 - MARGIN - MARGIN
    w = max(h, width_in_pixels(font, txt_1), width_in_pixels(font, txt_2), width_in_pixels(font, txt_3)) + padding
    fill_rect(cnv, x, y, w, h, color_bg)
    round_rect_corners(cnv, x, y, w, h)

    

    
    w_ = w
    h_ = h - padding - padding

    if txt_3:
        h_txt = int(h_ / 3)
        y_delta_txt = y_font_center(font, h_txt)
        x_txt_1 = x + padding + x_font_center(txt_1, w_, font)
        x_txt_2 = x + padding + x_font_center(txt_2, w_, font)
        x_txt_3 = x + padding + x_font_center(txt_3, w_, font)
        
        y_txt_1 = y + padding + y_delta_txt
        y_txt_2 = y + padding + y_delta_txt + h_txt
        y_txt_3 = y + padding + y_delta_txt + h_txt + h_txt

        #fill_rect(cnv, 0, y_txt_1, W_PANEL, 1, COLOR_RED)

        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, COLOR_TIME_BOX)
        draw_text(cnv, x_txt_2, y_txt_2, txt_2, font, COLOR_TIME_BOX)
        draw_text(cnv, x_txt_3, y_txt_3, txt_3, font, COLOR_TIME_BOX)
    
    elif txt_2:
        h_txt = int(h_ / 2)
        y_delta_txt = y_font_center(font, h_txt)
        x_txt_1 = x + padding + x_font_center(txt_1, w_, font)
        x_txt_2 = x + padding + x_font_center(txt_2, w_, font)
        y_txt_1 = y + padding * 2 + y_delta_txt
        y_txt_2 = y - padding * 2 + y_delta_txt + h_txt
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, COLOR_TIME_BOX)
        draw_text(cnv, x_txt_2, y_txt_2, txt_2, font, COLOR_TIME_BOX)    
    elif txt_1:
        h_txt = int(h_ / 1)
        y_delta_txt = y_font_center(font, h_txt)
        x_txt_1 = x + padding + x_font_center(txt_1, w_, font)
        y_txt_1 = y + padding + y_delta_txt
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, COLOR_TIME_BOX)

    return w

def _draw_booking_match(cnv, x0:int, y0:int, booking, caption=''):
    def booking_team(isTeam1=True):
        def booking_player(player):
            txt = None
            firstname = player.get('firstname')
            if firstname:
                txt = firstname
            else:
                lastname = player.get('lastname')
                if lastname:
                    if txt:
                        txt += ' '
                    txt += lastname
                else:
                    txt = _('booking.guest')
            return txt
        txt = None
        tp1 =  booking['p1'] if isTeam1 else booking.get('p3')
        if tp1:
            txt = booking_player(tp1)
        tp2 =  booking['p2'] if isTeam1 else booking.get('p4')
        if tp2:
            if txt:
                txt += ', '
            txt = (txt or '') + booking_player(tp2)
        return txt

    x = x0 + MARGIN
    y = y0 + MARGIN

    y += y_font_offset(FONT_BOOKING_CAPTION) + 1
    draw_text(cnv, x, y, caption, FONT_BOOKING_CAPTION, COLOR_BOOKING)
    y += 10

    txt = booking.get('display-text')
    if txt:
        MAX_ROW_LENGTH = 17
        row_1 = row_2 = ''
        for w in txt.split():
            if row_1:
                if len(row_1 + ' ' + w) <= MAX_ROW_LENGTH:
                    row_1 = row_1 + ' ' + w
                else:
                    row_2 = row_2 + (' ' if row_2 else '') + w
            else:
                row_1 = w
        logger.info(row_1)
        logger.info(row_2)
        y += y_font_offset(FONT_BOOKING_NAME)
        draw_text(cnv, x, y, row_1, FONT_BOOKING_NAME, COLOR_BOOKING)
        y += MARGIN * 2 + y_font_offset(FONT_BOOKING_NAME)
        draw_text(cnv, x, y, row_2, FONT_BOOKING_NAME, COLOR_BOOKING)
    else:    
        t1 = booking_team()
        y += y_font_offset(FONT_BOOKING_NAME)
        draw_text(cnv, x, y, t1, FONT_BOOKING_NAME, COLOR_BOOKING)
        y += MARGIN * 2

        t2 = booking_team(False)
        if t2:
            y += y_font_offset(FONT_BOOKING_NAME)
            draw_text(cnv, x, y, t2, FONT_BOOKING_NAME, COLOR_BOOKING)


def draw_ebusy_ads(cnv, ebusy_ads):
    id = ebusy_ads.get("id")
    url = ebusy_ads.get("url")
    path = IMAGE_CACHE_DIR + "/ebusy_" + str(id)

    try:
        if (os.path.isfile(path)):
            image = Image.open(path)
        else:
            image = Image.open(requests.get(url, stream=True).raw)            
            image.save(path, 'png')

        x = (W_PANEL - image.width) / 2
        y = (H_PANEL - image.height) / 2
        cnv.SetImage(image.convert('RGB'), x, y)

    except Exception as e:
        logger.debug(f"Error downloading image {url}", e)
        logger.exception(e)
        