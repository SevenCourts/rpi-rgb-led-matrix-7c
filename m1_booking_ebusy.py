from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import logging
import requests

# Style sheet
FONT_BOOKING = FONT_S
COLOR_BOOKING_GREETING = COLOR_7C_BLUE

BOOKIN_OVERLAP_MINUTES = 10

def draw_booking(canvas, booking, panel_tz):
    overlap_minutes_td = timedelta(minutes=BOOKIN_OVERLAP_MINUTES)
    court = booking.get('court')
    cur_booking = booking.get('current')
    next_booking = booking.get('next')
    
    # Use datetime set in admin panel UI for easier testing/debugging.
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
                    _display_booking_timeleft_match(canvas, cur_booking, court, t_now, minutes_left)
                else:
                    _display_booking_upcoming_match(canvas, next_booking, court, t_now)
            else:
                _display_booking_timeleft_match(canvas, cur_booking, court, t_now, minutes_left)
        else:
            _display_booking_greeting(canvas, cur_booking, court, t_now)
    elif next_booking and t_now >= (parser.parse(next_booking['start-date']) - overlap_minutes_td):
        _display_booking_upcoming_match(canvas, next_booking, court, t_now)

def _display_text(canvas, x, y, text):
    draw_text(canvas, x, y, text, FONT_BOOKING, COLOR_BOOKING_GREETING)

def _display_booking_header(canvas, court, dt):
    
    _display_text(canvas, 2, 10, court['name'])

    clock_str = dt.strftime('%H:%M')
    _display_text(canvas, 160, 10, clock_str)

def _display_booking_greeting(canvas, booking, court, dt):    

    _display_booking_header(canvas, court, dt)
    players = [p for p in [booking.get(k) for k in ['p1', 'p2', 'p3', 'p4']] if p]
    player_firstnames = [ p.get('firstname') for p in players]
    _display_text(canvas, 2, 25, 'Willkommen im MatchCenter')
    _display_text(canvas, 2, 40, ','.join(player_firstnames))

def _display_booking_timeleft_match(canvas, booking, court, dt, minutes_left):
    minutes_left_txt = '< 1' if minutes_left == 0 else str(minutes_left)
    _display_booking_match(canvas, booking, court, dt, 'Noch: ' + minutes_left_txt + ' min.')

def _display_booking_upcoming_match(canvas, booking, court, dt):
    _display_booking_match(canvas, booking, court, dt, 'Nachste')

def _display_booking_match(canvas, booking, court, dt, notification=''):
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

    _display_booking_header(canvas, court, dt)
    start_time = parser.parse(booking['start-date']).strftime('%H:%M')
    end_time = parser.parse(booking['end-date']).strftime('%H:%M')
    _display_text(canvas, 2, 25, start_time + ' - ' + end_time)

    t1 = booking_team()
    _display_text(canvas, 2, 40, t1)
    t2 = booking_team(False)
    if t2:
        _display_text(canvas, 2, 55, t2)

    if notification:
        _display_text(canvas, 105, 25, notification)

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
        logging.exception(e)
        logging.debug(f"Error downloading image {url}", e)