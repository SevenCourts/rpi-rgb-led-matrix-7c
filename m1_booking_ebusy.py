from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import requests

logger = m1_logging.logger("eBusy")

# Style sheet
FONT_COURT_NAME = FONT_S
FONT_CURRENT_TIME = FONT_S
FONT_TIME_BOX = FONT_S
FONT_BOOKING = FONT_S

COLOR_COURT_NAME = COLOR_WHITE
COLOR_CURRENT_TIME = COLOR_WHITE
COLOR_TIME_BOX = COLOR_WHITE
COLOR_BOOKING = COLOR_WHITE

COLOR_SEPARATOR_LINE = COLOR_7C_BLUE
COLOR_TIME_BOX_BG = COLOR_7C_GREEN


MARGIN = 2
H_HEADER = 12
W_TIME_BOX = 36
H_TIME_BOX = 36

BOOKING_OVERLAP_MINUTES = 10

def draw_booking(canvas, booking, panel_tz):
    overlap_minutes_td = timedelta(minutes=BOOKING_OVERLAP_MINUTES)
    court = booking.get('court')
    cur_booking = booking.get('current')
    next_booking = booking.get('next')
    
    # Use datetime set in the Panel Admin UI for easier testing/debugging:
    _dev_timestamp = booking.get('_dev_timestamp')
    if _dev_timestamp and len(_dev_timestamp):
        t_now = parser.parse(_dev_timestamp)
    else:
        t_now = datetime.now(tz.gettz(panel_tz))

    if cur_booking:
        t_end_right = parser.parse(cur_booking['end-date'])
        t_end_left = t_end_right - overlap_minutes_td

        if t_now >= t_end_left:
            minutes_left = (t_end_right - t_now).seconds // 60 % 60
            if next_booking:
                #  0 - 14 upcoming
                # 15 - 29 timeleft
                # 30 - 44 upcoming
                # 45 - 59 timeleft
                if (t_now.second >= 15 and t_now.second <= 29) or (t_now.second >= 45 and t_now.second <= 59):
                    _draw_timeleft(canvas, cur_booking, court, t_now, minutes_left)
                else:
                    _draw_upcoming(canvas, next_booking, court, t_now)
            else:
                _draw_timeleft(canvas, cur_booking, court, t_now, minutes_left)
        else:
            _draw_welcome(canvas, cur_booking, court, t_now)
    elif next_booking and t_now >= (parser.parse(next_booking['start-date']) - overlap_minutes_td):
        _draw_upcoming(canvas, next_booking, court, t_now)

def _draw_header(canvas, court, dt):
    """Retuns the y coordinate (height) of the header section"""        
    x_court_name = 0 + MARGIN
    y_court_name = y_font_offset(FONT_COURT_NAME) + MARGIN
    draw_text(canvas, x_court_name, y_court_name, court['name'], FONT_COURT_NAME, COLOR_COURT_NAME)

    clock_str = dt.strftime('%H:%M')
    x_clock = W_PANEL - MARGIN - width_in_pixels(FONT_CURRENT_TIME, clock_str)    
    y_clock =  y_font_offset(FONT_CURRENT_TIME) + MARGIN
    draw_text(canvas, x_clock, y_clock, clock_str, FONT_CURRENT_TIME, COLOR_CURRENT_TIME)

    y_separator = max(y_clock, y_court_name) + MARGIN
    graphics.DrawLine(canvas, 0, y_separator, W_PANEL, y_separator, COLOR_SEPARATOR_LINE)

    return y_separator

def _draw_welcome(canvas, booking, court, dt):    

    _draw_header(canvas, court, dt)
    players = [p for p in [booking.get(k) for k in ['p1', 'p2', 'p3', 'p4']] if p]

    player_firstnames = [ p.get('firstname') for p in players]

    draw_text(canvas, 2, 25, 'Willkommen', FONT_BOOKING, COLOR_BOOKING)
    draw_text(canvas, 2, 40, ', '.join(player_firstnames), FONT_BOOKING, COLOR_BOOKING)

def _draw_timeleft(canvas, booking, court, dt, minutes_left):
    minutes_left_txt = '< 1' if minutes_left == 0 else str(minutes_left)
    _draw_booking_match(canvas, booking, court, dt, 'Noch: ' + minutes_left_txt + ' min.')

def _draw_upcoming(canvas, booking, court, dt):
    _draw_booking_match(canvas, booking, court, dt, 'Nachste')

def _draw_booking_match(canvas, booking, court, dt, notification=''):
    def booking_team(isTeam1=True):
        def booking_player(player):
            txt = None
            firstname = player.get('firstname')
            if firstname:
                txt = firstname
            lastname = player.get('lastname')
            if lastname:
                if txt:
                    txt += ' '
                txt += lastname
            return txt

        txt = None
        tp1 =  booking['p1'] if isTeam1 else booking.get('p3')
        if tp1:
            txt = booking_player(tp1)
        tp2 =  booking['p2'] if isTeam1 else booking.get('p4')
        if tp2:
            if txt:
                txt += ' und '
            txt = (txt or '') + booking_player(tp2)
        return txt

    _draw_header(canvas, court, dt)
    start_time = parser.parse(booking['start-date']).strftime('%H:%M')
    end_time = parser.parse(booking['end-date']).strftime('%H:%M')
    draw_text(canvas, 2, 25, start_time + ' - ' + end_time, FONT_TIME_BOX, COLOR_TIME_BOX)

    t1 = booking_team()
    draw_text(canvas, 2, 40, t1, FONT_BOOKING, COLOR_BOOKING)
    t2 = booking_team(False)
    if t2:
        draw_text(canvas, 2, 55, t2, FONT_BOOKING, COLOR_BOOKING)

    if notification:
        draw_text(canvas, 105, 25, notification, FONT_BOOKING, COLOR_BOOKING)

def draw_ebusy_ads(canvas, ebusy_ads):
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
        canvas.SetImage(image.convert('RGB'), x, y)

    except Exception as e:
        logger.debug(f"Error downloading image {url}", e)
        logger.exception(e)
        