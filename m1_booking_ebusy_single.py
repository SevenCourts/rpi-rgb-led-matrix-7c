from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import m1_clock
import m1_image
from m1_booking_utils import *
from m1_club_styles import *

logger = m1_logging.logger("eBuSy")

Y_PROMPT = H_PANEL - 3 # "Bye" - the 'y' takes 3 pixels for the tail

def draw(cnv, booking_info, panel_tz, s: ClubStyle):

    court_bookings = booking_info['courts'][0]
    court = court_bookings['court']
    b_0_past = court_bookings['past']
    b_1_current = court_bookings['current']
    b_2_next = court_bookings['next']

    # header
    h_header = y_font_offset(s.booking.one.f_courtname_on_top) + 4

    # clock        
    ## Use datetime set in the Panel Admin UI for easier testing/debugging:
    _dev_timestamp = booking_info.get('_dev_timestamp')
    if _dev_timestamp and len(_dev_timestamp):
        time_now = parser.parse(_dev_timestamp)
    else:
        time_now = datetime.now(tz.gettz(panel_tz))

    ## draw clock
    f_clock = s.booking.f_clock
    c_clock = s.booking.c_clock
    w_clock = width_in_pixels(f_clock, "00:00") - 2 # px to the right are empty
    x_clock = W_PANEL - w_clock
    y_clock = H_PANEL
    
    x_timebox = x_clock
    w_timebox = w_clock
    c_timebox = s.booking.c_timebox

    txts_timebox = ('', '')
    txt_prompt = ''
    booking = None
    
    if b_0_past and not b_1_current:
        # Show "Game over" for 2 minutes only if there is no current booking
        t_0_4_gameover_end = (parser.parse(b_0_past['end-date']) + TD_4_GAMEOVER)
        if time_now < t_0_4_gameover_end:
            txts_timebox = ('Game', 'over')
            txt_prompt = 'Bye!'
            booking = b_0_past

    elif b_1_current:
        # current booking

        t_start = parser.parse(b_1_current['start-date'])
        t_end = parser.parse(b_1_current['end-date'])

        t_0_upcoming_start = (t_start + TD_0_UPCOMING)
        t_1_welcome_end = (t_start + TD_1_WELCOME)
        t_3_countdown_start = (t_end + TD_3_COUNTDOWN)

        logger.debug(time_now)
        logger.debug(t_3_countdown_start)        

        if time_now < t_3_countdown_start:
            c_timebox = s.booking.c_timebox
        elif time_now < t_end:
            c_timebox = s.booking.c_timebox_countdown            
        else:
            # raise ValueError('should never happen with eBuSy data')
            '''
            This data is twice formally incorrect:

            For 2025-08-28T22:00:00

            1) end date should be "end-date": "2025-08-28T22:00:00"
            2) start time of the next booking is the same as the end time of the current booking

            "past": {                
                "start-date": "2025-08-28T20:00:00"
                "end-date": "2025-08-28T22:00:00"
            },
            "current": {
                "start-date": "2025-08-28T22:00:00"
                "end-date": "2025-08-28T00:00:00"                
            }

            start: 2025-08-28 22:00:00
            end:   2025-08-28 00:00:00 (!!)
            t0:   2025-08-28 21:55
            t1:   2025-08-28 22:02
            t3:   2025-08-27 23:55 (!!!)
            '''
            c_timebox = s.booking.c_timebox

        
        if time_now > t_0_upcoming_start:
            (hours_left, minutes_in_hour_left) = hours_minutes_diff(t_end, time_now)
            if hours_left > 0:
                txts_timebox = (f">{hours_left}h", '')
            else:
                txts_timebox = (f" {minutes_in_hour_left}'", '')
            
            if time_now < t_1_welcome_end:
                booking = b_1_current
                # txt_prompt = 'Push any button to start keeping score'
                # txt_prompt = 'Eine Taste am Netz drücken, um zu starten'
                txt_prompt = 'Have fun!'    
            elif time_now < t_3_countdown_start:
                booking = b_1_current
            elif time_now < t_end:
                c_timebox = s.booking.c_timebox_countdown
                # Adjacent bookings handling: interchange every 10 seconds
                if b_2_next and is_current_second_in_period(time_now, PERIOD_INTERCHANGE_ADJACENT_S):
                    # next booking
                    booking = b_2_next
                    txt_prompt = 'Next booking'                    
                    t_start = parser.parse(booking['start-date'])
                    t_end = parser.parse(booking['end-date'])
                    txts_timebox = (t_start.strftime('%H:%M'), t_end.strftime('%H:%M'))
                else:
                    # current booking
                    booking = b_1_current                    
            else:
                logger.error('should never happen with eBuSy data', ValueError('should never happen with eBuSy data'))
            
        else:
            logger.error('should never happen with eBuSy data', ValueError('should never happen with eBuSy data'))
            

    elif b_2_next:
        # next booking
        c_timebox = s.booking.c_timebox_countdown
        booking = b_2_next
        txt_prompt = 'Next booking'
        t_start = parser.parse(booking['start-date'])
        t_end = parser.parse(booking['end-date'])
        txts_timebox = (t_start.strftime('%H:%M'), t_end.strftime('%H:%M'))
    else:
        # court is free
        txt_prompt = 'Book now with code 7CAB for 10% discount'
        txt_prompt = 'Book now via eBuSy'

    h_prompt = 2 * y_font_offset(s.booking.one.f_prompt) + 4
    y_prompt = H_PANEL - h_prompt
    
    if s.booking.one.is_court_name_on_top:
        txt_court = court['name']
        # txt_court = txt_court.replace("Platz", "Court") # FIXME EN demo only, remove ".replace"

        f_court = s.booking.one.f_courtname_on_top
        w_court = W_PANEL
        h_court = h_header
        w_info = W_PANEL - w_timebox
        x_info = 0
        y_info = y_timebox = h_header
        
        h_timebox = h_info = H_PANEL - h_header - h_prompt

        w_prompt = W_PANEL - w_clock

        h_courtname_text = h_header
    else:
        txt_court = court['shortName']
        txt_court = txt_court[:s.booking.courtname_truncate_to]

        f_court = s.booking.one.f_courtname_on_left

        w_court = width_in_pixels(f_court, txt_court) + 3
        h_court = H_PANEL

        x_info = w_court
        w_info = W_PANEL - w_timebox - w_court
        y_info = y_timebox = 0
        
        h_timebox = h_info = H_PANEL - h_prompt

        w_prompt = W_PANEL - w_clock - w_court
    

    if booking:
        ((txt_1, txt_2), _) = booking_info_texts(booking, w_info - 2, (s.booking.one.f_info, s.booking.one.f_info))
        c_info = s.ci.c_text
    else:
        txt_1, txt_2 = ('Free till 16h00', '') # TODO i18n TODO till?
        txt_1, txt_2 = ('Free', '') # TODO i18n
        c_info = s.booking.c_free_to_book
    
    if not s.booking.one.is_court_name_on_top:
        h_courtname_text = (h_info // 2 + 5) if txt_2 else h_info



    m1_clock.draw_clock_by_coordinates(cnv, x_clock, y_clock, f_clock, panel_tz, c_clock, time_now)
    _draw_court(cnv, 0, 0, w_court, h_court, h_courtname_text, txt_court, f_court, s)
    _draw_timebox(cnv, x_timebox, y_timebox, w_timebox, h_timebox, txts_timebox, c_timebox, s)
    _draw_info(cnv, x_info, y_info, w_info, h_info, txt_1, txt_2, c_info, s)
    _draw_prompt(cnv, x_info, y_prompt, w_prompt, h_prompt, txt_prompt, s)


def _draw_court(cnv, x0: int, y0: int, w: int, h: int, h_courtname_text: int, txt: str, fnt: graphics.Font, s: ClubStyle):
    """Retuns the y coordinate (height) of the header section"""

    if False:
        fill_rect(cnv, x0, y0, w, h, COLOR_MAGENTA)

    fill_rect(cnv, x0, y0, w, h, s.ci.c_bg_1)

    if s.booking.one.is_court_name_on_top:
        # top        
        _w = w - 2
        _x = x0 + 1
        _y = y0 + y_font_center(fnt, h) - 1
        y_separator = h - 1

        txt = ellipsize(txt, _w, fnt)
        
        draw_text(cnv, _x, _y, txt, fnt, s.ci.c_text)
        graphics.DrawLine(cnv, 0, y_separator, W_PANEL, y_separator, s.ci.c_bg_2)
    else:
        # left
        _w = w - 2
        _x = x0 + 1
        _y = y0 + y_font_center(fnt, h_courtname_text)
        #_y = y0 + y_font_offset(fnt) + 1
        x_separator = x0 + w - 1
        y_separator = y0 + h

        draw_text(cnv, _x, _y, txt, fnt, s.ci.c_text)        
        graphics.DrawLine(cnv, x_separator, 0, x_separator, y_separator, s.ci.c_bg_2)


def _draw_timebox(cnv, x0:int, y0:int, w:int, h:int,
                  texts: tuple[str, str], 
                  color: graphics.Color, s: ClubStyle):
    
    if False:
        fill_rect(cnv, x0, y0, w, h, COLOR_MAGENTA)

    txt_1, txt_2 = texts

    font = s.booking.one.f_timebox
    padding = 2
    
    x = x0 + padding
    y = y0 + padding
    _w = w - padding*2
    _h = h - padding*2

    if txt_2:
        draw_rect(cnv, x, y, _w, _h, s.ci.c_bg_1, round_corners=True)
        h_txt = _h // 2
        y_delta_txt = y_font_center(font, h_txt)
        x_txt_1 = x + x_font_center(txt_1, _w, font)
        x_txt_2 = x + x_font_center(txt_2, _w, font)
        y_txt_1 = y + y_delta_txt + 1
        y_txt_2 = y + y_delta_txt + h_txt - 1
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, color)
        draw_text(cnv, x_txt_2, y_txt_2, txt_2, font, color)    
    elif txt_1:
        draw_rect(cnv, x, y, _w, _h, s.ci.c_bg_1, round_corners=True)
        h_txt = _h // 1
        y_delta_txt = y_font_center(font, h_txt)
        x_txt_1 = x + x_font_center(txt_1, _w, font)
        y_txt_1 = y + y_delta_txt
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, color)
    else:
        _draw_logo(cnv, x0, y0, w, h, s.ci.logo.path, s)

def _draw_logo(cnv, x0, y0, w, h, logo_path, s: ClubStyle):

    if False:
        fill_rect(cnv, x0, y0, w, h, COLOR_MAGENTA)

    _w = w - 2
    _h = h - 4

    image = Image.open(logo_path)
    m1_image.thumbnail(image, _w, _h)

    _y = y0 + 2 + (_h - image.height) // 2
    _x = x0 + 1 + (_w - image.width) // 2

    cnv.SetImage(image.convert('RGB'), _x, _y)
    if s.ci.logo.round_corners:
        round_rect_corners(cnv, _x, _y, image.width, image.height)


def _draw_info(cnv, x0: int, y0: int, w: int, h: int, txt_1: str, txt_2: str, clr: graphics.Color, s: ClubStyle):

    if False:
        fill_rect(cnv, x0, y0, w, h, COLOR_MAGENTA)

    x = x0 + 2
    y = y0 + 3
    
    fnt = s.booking.one.f_info
    
    h_row = (h - 6) // 2
    
    if txt_1:
        if txt_2:
            _y = y + y_font_center(fnt, h_row) + 1
            draw_text(cnv, x, _y, txt_1, fnt, clr)
            _y = y + h_row + y_font_center(fnt, h_row)
            draw_text(cnv, x, _y, txt_2, fnt, clr)
        else:
            _y = y + y_font_center(fnt, h_row * 2)
            draw_text(cnv, x, _y, txt_1, fnt, clr)


def _draw_prompt(cnv, x0, y0, w, h, text: str, s: ClubStyle):

    if False:
        fill_rect(cnv, x0, y0, w, h, COLOR_GREEN)

    t1, t2 = truncate_into_rows(text, w, s.booking.one.f_prompt, 2, True)

    if not t2:
        t2 = t1
        t1 = ''
    
    fnt = s.booking.one.f_prompt
    clr = s.booking.one.c_prompt

    y = y0
    x = x0 + 1
    
    y += y_font_offset(fnt)
    draw_text(cnv, x, y, t1, fnt, clr)

    y += y_font_offset(fnt) + 2 - (2 if not t1 else 0)
    draw_text(cnv, x, y, t2, fnt, clr)
