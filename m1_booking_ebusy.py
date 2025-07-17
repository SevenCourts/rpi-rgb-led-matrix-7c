from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import requests
import m1_clock
import m1_image

logger = m1_logging.logger("eBusy")

# Style sheet
FONT_COURT_NAME = FONT_S
FONT_CURRENT_TIME = FONT_S
FONT_TIME_BOX = FONT_M
FONT_BOOKING = FONT_S
FONT_MESSAGE = FONT_M

COLOR_HEADER_BG = COLOR_GREY_DARKEST

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

def draw_booking(cnv, booking, panel_tz):
    court = booking.get('court')
    cur_booking = booking.get('current')
    next_booking = booking.get('next')
    
    # Use datetime set in the Panel Admin UI for easier testing/debugging:
    _dev_timestamp = booking.get('_dev_timestamp')
    if _dev_timestamp and len(_dev_timestamp):
        t = parser.parse(_dev_timestamp)
    else:
        t = datetime.now(tz.gettz(panel_tz))
    
    if cur_booking:
        h_header = _draw_header(cnv, court, t)

        t_start = parser.parse(cur_booking['start-date'])
        t_end = parser.parse(cur_booking['end-date'])

        t_0_upcoming_start = (t_start + TD_0_UPCOMING)        
        t_1_welcome_end = (t_start + TD_1_WELCOME)
        t_3_countdown_start = (t_end + TD_3_COUNTDOWN)
        
        if t > t_0_upcoming_start:


            # 1. time box
            if t < t_3_countdown_start:
                w_timebox = _draw_time_box(cnv, h_header, COLOR_TIME_BOX_BG_INFO, t_start.strftime('%H:%M'), "-", t_end.strftime('%H:%M'))                
            elif t < t_end:
                minutes_left = (t_end - t).seconds // 60 % 60
                minutes_left_txt = '< 1' if minutes_left == 0 else str(minutes_left)
                w_timebox = _draw_time_box(cnv, h_header, COLOR_TIME_BOX_BG_WARN, 'Noch', f"{minutes_left_txt} min")
            else:
                # should never happen with eBusy data
                w_timebox = _draw_time_box(cnv, h_header, COLOR_TIME_BOX_BG_INFO, 'Hi :)')


            # 2. message area
            x0 = w_timebox + MARGIN * 2
            if t < t_start:
                logger.debug("0 - upcoming")
                _draw_booking_match(cnv, x0, h_header, cur_booking, 'UPCOMING')
            elif t < t_1_welcome_end:                
                logger.debug("1 - welcome")
                _draw_booking_match(cnv, x0, h_header, cur_booking, 'WELCOME')
            elif t < t_3_countdown_start:
                logger.debug("2 - default")
                _draw_booking_match(cnv, x0, h_header, cur_booking)
            elif t < t_end:
                logger.debug("3 - countdown")
                _draw_booking_match(cnv, x0, h_header, cur_booking, 'COUNTDOWN')
            
        # Adjacent bookings handling (old code)
        '''
        if t_now >= (t_end - TD_1_WELCOME):
            minutes_left = (t_end - t_now).seconds // 60 % 60
            if next_booking:
                #  0 - 14 upcoming
                # 15 - 29 timeleft
                # 30 - 44 upcoming
                # 45 - 59 timeleft
                if (t_now.second >= 15 and t_now.second <= 29) or (t_now.second >= 45 and t_now.second <= 59):
                    _draw_3_timeleft(cnv, cur_booking, court, t_now, minutes_left)
                else:
                    _draw_0_upcoming(cnv, next_booking, court, t_now)
            else:
                _draw_3_timeleft(cnv, cur_booking, court, t_now, minutes_left)
        else:
            _draw_1_welcome(cnv, cur_booking)
    elif next_booking and t_now >= (parser.parse(next_booking['start-date']) - TD_1_WELCOME):
        _draw_0_upcoming(cnv, next_booking, court, t_now)
    '''
    else:
        h_header = _draw_header(cnv, court)

        h_logo = H_PANEL - h_header - MARGIN - MARGIN



        # no current booking - show a default
        image = Image.open('images/logos/SV1845/sv1845_76x64_eBusy_demo_logo.png')
        m1_image.thumbnail(image, h = h_logo)

        x = MARGIN
        y = h_header + MARGIN
        cnv.SetImage(image.convert('RGB'), x, y)

        round_rect_corners(cnv, x, y, image.width, image.height)

        text = t.strftime('%H:%M')
        text = "22:22"
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
    x = MARGIN
    y = y0 + MARGIN
    h = H_PANEL - y0 - MARGIN - MARGIN
    w = h
    fill_rect(cnv, x, y, w, h, color_bg)
    round_rect_corners(cnv, x, y, w, h)

    padding = MARGIN
    w_ = w
    h_ = h - padding - padding

    if txt_3:
        h_txt = int(h_ / 3)
        y_delta_txt = y_font_center(FONT_TIME_BOX, h_txt)
        x_txt_1 = x + x_font_center(txt_1, w_, FONT_TIME_BOX)
        x_txt_2 = x + x_font_center(txt_2, w_, FONT_TIME_BOX)
        x_txt_3 = x + x_font_center(txt_3, w_, FONT_TIME_BOX)
        
        y_txt_1 = y + padding + y_delta_txt
        y_txt_2 = y + padding + y_delta_txt + h_txt
        y_txt_3 = y + padding + y_delta_txt + h_txt + h_txt

        #fill_rect(cnv, 0, y_txt_1, W_PANEL, 1, COLOR_RED)

        draw_text(cnv, x_txt_1, y_txt_1, txt_1, FONT_TIME_BOX, COLOR_TIME_BOX)
        draw_text(cnv, x_txt_2, y_txt_2, txt_2, FONT_TIME_BOX, COLOR_TIME_BOX)
        draw_text(cnv, x_txt_3, y_txt_3, txt_3, FONT_TIME_BOX, COLOR_TIME_BOX)
    
    elif txt_2:
        h_txt = int(h_ / 2)
        y_delta_txt = y_font_center(FONT_TIME_BOX, h_txt)
        x_txt_1 = x + x_font_center(txt_1, w_, FONT_TIME_BOX)
        x_txt_2 = x + x_font_center(txt_2, w_, FONT_TIME_BOX)
        y_txt_1 = y + padding * 2 + y_delta_txt
        y_txt_2 = y - padding * 2 + y_delta_txt + h_txt
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, FONT_TIME_BOX, COLOR_TIME_BOX)
        draw_text(cnv, x_txt_2, y_txt_2, txt_2, FONT_TIME_BOX, COLOR_TIME_BOX)    
    elif txt_1:
        h_txt = int(h_ / 1)
        y_delta_txt = y_font_center(FONT_TIME_BOX, h_txt)
        x_txt_1 = x + x_font_center(txt_1, w_, FONT_TIME_BOX)
        y_txt_1 = y + padding + y_delta_txt
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, FONT_TIME_BOX, COLOR_TIME_BOX)


    return w
        

def _draw_2_default(cnv, x0, y0, booking):
    _draw_1_welcome(cnv, x0, y0, booking)

def _draw_1_welcome(cnv, x0, y0, booking):

    x = x0 + MARGIN
    y = y0 + MARGIN * 2
    
    players = [p for p in [booking.get(k) for k in ['p1', 'p2', 'p3', 'p4']] if p]

    player_firstnames = [ p.get('firstname') for p in players]

    y_1 = y + y_font_offset(FONT_BOOKING)
    y_2 = y_1 + y_font_offset(FONT_BOOKING) * 3

    draw_text(cnv, x, y_1, 'Willkommen zum SV1845!', FONT_BOOKING, COLOR_BOOKING)
    draw_text(cnv, x, y_2, ', '.join(player_firstnames), FONT_BOOKING, COLOR_BOOKING)

def _draw_booking_match(cnv, x0:int, y0:int, booking, notification=''):
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
                    txt = "n.A."
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

    if notification:
        y += y_font_offset(FONT_BOOKING)
        draw_text(cnv, x, y, notification, FONT_BOOKING, COLOR_BOOKING)
        y += MARGIN
    
    t1 = booking_team()
    y += y_font_offset(FONT_BOOKING)
    draw_text(cnv, x, y, t1, FONT_BOOKING, COLOR_BOOKING)
    y += MARGIN

    t2 = booking_team(False)
    if t2:
        y += y_font_offset(FONT_BOOKING)
        draw_text(cnv, x, y, t2, FONT_BOOKING, COLOR_BOOKING)


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
        