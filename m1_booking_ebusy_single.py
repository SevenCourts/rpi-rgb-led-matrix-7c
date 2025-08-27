from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import gettext
import m1_clock
import m1_image
from m1_booking_utils import *
from m1_club_styles import *

logger = m1_logging.logger("eBusy")

Y_PROMPT = H_PANEL - 3 # "Bye" - the 'y' takes 3 pixels for the tail

def draw(cnv, booking_info, panel_tz, s: ClubStyle):

    court_bookings = booking_info['courts'][0]
    court = court_bookings['court']
    b_0_past = court_bookings['past']
    b_1_current = court_bookings['current']
    b_2_next = court_bookings['next']

    # header
    h_header = _draw_header(cnv, court, s)

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
    w_clock = width_in_pixels(f_clock, "00:00")
    x_clock = W_PANEL - w_clock
    h_clock = y_font_offset(f_clock) + 1
    y_clock = H_PANEL - 1
    m1_clock.draw_clock_by_coordinates(cnv, x_clock, y_clock, f_clock, panel_tz, c_clock, time_now)


    x_logo = x_timebox = x_clock
    w_logo = w_timebox = w_clock
    h_logo = h_timebox = H_PANEL - h_header - h_clock

    x_match = 0
    w_match = W_PANEL - w_timebox
    
    txt_timebox = txt_prompt = ('', '')
    booking = None
    
    if b_0_past and not b_1_current:
        # Show "Game over" for 2 minutes only if there is no current booking
        t_0_4_gameover_end = (parser.parse(b_0_past['end-date']) + TD_4_GAMEOVER)
        if time_now < t_0_4_gameover_end:
            txt_timebox = ('Game', 'over')
            txt_prompt = 'Bye!'
            booking = b_0_past
            
            #_draw_timebox(cnv, x_timebox, h_header, w_timebox, h_timebox, s, s.booking.c_timebox, 
            #               ('Game', 'over')) # TODO i18n
            #_draw_match(cnv, s, x_match, h_header, w_match, b_0_past, 
            #                    'Bye!') # TODO i18n

    elif b_1_current:
        
        t_start = parser.parse(b_1_current['start-date'])
        t_end = parser.parse(b_1_current['end-date'])

        t_0_upcoming_start = (t_start + TD_0_UPCOMING)
        t_1_welcome_end = (t_start + TD_1_WELCOME)
        t_3_countdown_start = (t_end + TD_3_COUNTDOWN)

        if time_now < t_3_countdown_start:
            c_timebox = s.booking.c_timebox
        elif time_now < t_end:
            c_timebox = s.booking.c_timebox_countdown            
        else:
            raise ValueError('should never happen with eBusy data')
        
        if time_now > t_0_upcoming_start:
            # 1. time box
            
            (hours_left, minutes_in_hour_left) = hours_minutes_diff(t_end, time_now)

            if hours_left > 0:
                txt_timebox = (f">{hours_left}h", '')
            else:
                txt_timebox = (f" {minutes_in_hour_left}'", '')
            

            #_draw_timebox(cnv, x_timebox, h_header, w_timebox, h_timebox, s, c_timebox, 
            #                (txt_timebox, ''))
            
            # 2.match area
            if time_now < t_1_welcome_end:
                booking = b_1_current
                txt_prompt = 'Push any button to start keeping score'
                txt_prompt = 'Have fun!'
                #_draw_match(cnv, s, x_match, h_header, w_match, b_1_current,
                #            'Push button to start')
                #                    #'Have fun!') # TODO i18n
            elif time_now < t_3_countdown_start:
                booking = b_1_current
                #_draw_match(cnv, s, x_match, h_header, w_match, b_1_current)
            elif time_now < t_end:
                # Adjacent bookings handling: interchange every 10 seconds
                if b_2_next and is_current_second_in_period(PERIOD_INTERCHANGE_ADJACENT_S, time_now):
                    booking = b_2_next
                    txt_prompt = 'Next booking'
                    #_draw_match(cnv, s, x_match, h_header, w_match, b_2_next, 'Next booking') # TODO i18n             
                else:
                    booking = b_1_current
                    #_draw_match(cnv, s, x_match, h_header, w_match, b_1_current)
            else:
                raise ValueError('should never happen with eBusy data')
        else:
            raise ValueError('should never happen with eBusy data')

    elif b_2_next:
        t_start = parser.parse(b_2_next['start-date'])
        t_end = parser.parse(b_2_next['end-date'])

        booking = b_2_next
        txt_timebox = (t_start.strftime('%H:%M'), t_end.strftime('%H:%M'))
        txt_prompt = 'Next booking'

        #_draw_timebox(cnv, x_timebox, h_header, w_timebox, h_timebox, s, s.booking.c_timebox, 
        #               (t_start.strftime('%H:%M'), t_end.strftime('%H:%M')))
        #_draw_match(cnv, s, x_match, h_header, w_match, b_2_next, 'Next booking') # TODO i18n

    else:
        # Free court: show a logo and "Free" text with "Book me!" prompt

        _w = w_logo - 2
        _h = h_logo - 2
        
        image = Image.open(s.ci.logo.path)
        m1_image.thumbnail(image, _w, _h)

        _y = h_header + 1 + (_h - image.height) // 2
        _x = x_logo + 1 + (_w - image.width) // 2

        cnv.SetImage(image.convert('RGB'), _x, _y)
        if s.ci.logo.round_corners:
            round_rect_corners(cnv, _x, _y, image.width, image.height)

        txt_prompt = 'Book now'
        txt_prompt = 'Book now with code FG38 for 10% discount'

        #prompt = "Book now: 10% discount" # TODO i18n
        #prompt = "Book now!" # TODO i18n
        #fnt = s.booking.one.f_prompt
        #draw_text(cnv, x_txt_free_court, Y_PROMPT, prompt, fnt, s.booking.one.c_prompt)

    h_prompt = 2 * y_font_offset(s.booking.one.f_prompt) + 5
    y_prompt = H_PANEL - h_prompt
    w_prompt = W_PANEL - w_clock

    h_match = H_PANEL - h_header - h_prompt

    txt_prompt = 'Book now with code 7CAB for 10% discount!'
    #txt_prompt = 'Book now!'
    

    _draw_timebox(cnv, x_timebox, h_header, w_timebox, h_timebox, s, s.booking.c_timebox, txt_timebox)
    _draw_match(cnv, s, x_match, h_header, w_match, h_match, booking)
    _draw_prompt(cnv, x_match, y_prompt, w_prompt, h_prompt, txt_prompt, s)


def _draw_prompt(cnv, x0, y0, w, h, text: str, s: ClubStyle):

    if False:
        fill_rect(cnv, x0, y0, w, h, COLOR_MAGENTA)

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

    y += y_font_offset(fnt) + 3
    draw_text(cnv, x, y, t2, fnt, clr)



def _draw_header(cnv, court, s: ClubStyle):
    """Retuns the y coordinate (height) of the header section"""        
    f_name = s.booking.one.f_courtname
    
    mrgn = 2
    _y = y_font_offset(f_name) + mrgn        
    y_separator = _y + mrgn
    fill_rect(cnv, 0, 0, W_PANEL, y_separator, s.ci.c_bg_1)

    w_court_name = W_PANEL - mrgn*2
    
    txt = ellipsize(court['name'], w_court_name, f_name)

    _x = max(0 + mrgn, W_PANEL - width_in_pixels(f_name, txt) - mrgn)
    if txt != court['name']:
        # ellipsize
        txt = txt[:len(txt)-1] + SYMBOL_ELLIPSIS
    draw_text(cnv, _x, _y, txt, f_name, s.ci.c_text)

    graphics.DrawLine(cnv, 0, y_separator, W_PANEL, y_separator, s.ci.c_bg_2)

    return y_separator + 1

def _draw_timebox(cnv, x0:int, y0:int, w:int, h:int, s: ClubStyle, 
                  color:graphics.Color, texts: tuple[str, str, str]):
    
    if False:
        fill_rect(cnv, x0, y0, w, h, COLOR_MAGENTA)

    (txt_1, txt_2) = texts

    font = s.booking.one.f_timebox
    padding = 2
    
    x = x0 + padding
    y = y0 + padding
    _w = w - padding*2
    _h = h - padding*2

    draw_rect(cnv, x, y, _w, _h, s.ci.c_bg_1, round_corners=True)

    if txt_2:
        h_txt = int(_h / 2)
        y_delta_txt = y_font_center(font, h_txt)
        x_txt_1 = x + x_font_center(txt_1, _w, font)
        x_txt_2 = x + x_font_center(txt_2, _w, font)
        y_txt_1 = y + y_delta_txt + 2
        y_txt_2 = y + y_delta_txt + h_txt - 1
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, color)
        draw_text(cnv, x_txt_2, y_txt_2, txt_2, font, color)    
    elif txt_1:
        h_txt = int(_h / 1)
        y_delta_txt = y_font_center(font, h_txt)
        x_txt_1 = x + x_font_center(txt_1, _w, font)
        y_txt_1 = y + y_delta_txt
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, color)


def _draw_match(cnv, s: ClubStyle, x0: int, y0: int, w: int, h: int, booking):

    if True:
        fill_rect(cnv, x0, y0, w, h, COLOR_MAGENTA)

    x = x0 + 1
    y = y0
    
    fnt = s.booking.one.f_info
    
    h_row = y_font_offset(fnt) + 5
    w_row = w - 5 # experimental magic value ;)


    if False:
        fill_rect(cnv, x0, y0, w, h, COLOR_MAGENTA)
    
    # info (up to 2 lines)
    if booking:
        (txt_1, txt_2) = booking_info_texts(booking, w_row, fnt)
        clr = s.ci.c_text
    else:
        (txt_1, txt_2) = ('Free', '') # TODO i18n
        clr = s.booking.c_free_to_book

    if txt_1:
        if txt_2:
            _y = y + h_row
            draw_text(cnv, x, _y, txt_1, fnt, clr)
            _y = y + h_row * 2
            draw_text(cnv, x, _y, txt_2, fnt, clr)
        else:
            _y = y + y_font_center(fnt, h_row * 2)
            draw_text(cnv, x, _y, txt_1, fnt, clr)
