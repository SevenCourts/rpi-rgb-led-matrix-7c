from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import gettext
import m1_clock
import m1_image
from m1_booking_utils import *
from m1_club_styles import *

logger = m1_logging.logger("eBusy")

def draw(cnv, booking_info, panel_tz, s: ClubStyle):

    mrgn = 2
    
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
    x_clock = W_PANEL - width_in_pixels(f_clock, "00:00")
    h_clock = y_font_offset(f_clock) + 1
    y_clock = H_PANEL - 1
    m1_clock.draw_clock_by_coordinates(cnv, x_clock, y_clock, f_clock, panel_tz, c_clock, time_now)


    c_timebox_warn = s.booking.c_timebox_countdown
    c_timebox = s.booking.c_timebox

    if b_0_past and not b_1_current:
        # Show "Game over" for 2 minutes only if there is no current booking
        t_0_4_gameover_end = (parser.parse(b_0_past['end-date']) + TD_4_GAMEOVER)
        if time_now < t_0_4_gameover_end:
            w_timebox = _draw_time_box(cnv, h_header, s, c_timebox, 'Game', 'over') # TODO i18n
            x = w_timebox + mrgn
            _draw_booking_match(cnv, s, x, h_header, b_0_past, 'Bye!') # TODO i18n

    elif b_1_current:
        
        t_start = parser.parse(b_1_current['start-date'])
        t_end = parser.parse(b_1_current['end-date'])

        t_0_upcoming_start = (t_start + TD_0_UPCOMING)
        t_1_welcome_end = (t_start + TD_1_WELCOME)
        t_3_countdown_start = (t_end + TD_3_COUNTDOWN)
        
        if time_now > t_0_upcoming_start:
            # 1. time box
            if time_now < t_3_countdown_start:
                w_timebox = _draw_time_box(cnv, h_header, s, c_timebox, t_start.strftime('%H:%M'), "-", t_end.strftime('%H:%M'))
            elif time_now < t_end:
                minutes_left = (t_end - time_now).seconds // 60 % 60 + 1
                if minutes_left == 0:
                    w_timebox = _draw_time_box(cnv, h_header, s, c_timebox_warn, 'Last', 'minute') # TODO i18n
                else:
                    w_timebox = _draw_time_box(cnv, h_header, s, c_timebox_warn, f"{minutes_left} min")
            else:
                raise ValueError('should never happen with eBusy data')

            # 2. message area
            x = w_timebox + mrgn
            if time_now < t_1_welcome_end:                
                _draw_booking_match(cnv, s, x, h_header, b_1_current, 'Have fun!') # TODO i18n
            elif time_now < t_3_countdown_start:
                _draw_booking_match(cnv, s, x, h_header, b_1_current)
            elif time_now < t_end:
                # Adjacent bookings handling: interchange every 10 seconds
                if b_2_next and is_current_second_in_period(PERIOD_INTERCHANGE_ADJACENT_S, time_now):
                    _draw_booking_match(cnv, s, x, h_header, b_2_next, 'Next booking') # TODO i18n             
                else:
                    _draw_booking_match(cnv, s, x, h_header, b_1_current)
            else:
                raise ValueError('should never happen with eBusy data')
        else:
            raise ValueError('should never happen with eBusy data')

    elif b_2_next:
        t_start = parser.parse(b_2_next['start-date'])
        t_end = parser.parse(b_2_next['end-date'])
        w_timebox = _draw_time_box(cnv, h_header, s, c_timebox, t_start.strftime('%H:%M'), "-", t_end.strftime('%H:%M'))
        x = w_timebox + mrgn
        _draw_booking_match(cnv, s, x, h_header, b_2_next, 'Next booking') # TODO i18n

    else:
        # no bookings - show a logo and "Free" text
        image = Image.open(s.ci.logo.path)
        MAX_IMAGE_WIDTH = 76 # so that 22:22 time fits
        h_logo = H_PANEL - h_header - mrgn
        m1_image.thumbnail(image, MAX_IMAGE_WIDTH, h_logo)
        x = 0
        y = h_header + (h_logo - image.height) // 2 + 1
        cnv.SetImage(image.convert('RGB'), x, y)
        if s.ci.logo.round_corners:
            round_rect_corners(cnv, x, y, image.width, image.height)

        txt = "Free to book" # TODO i18n
        fnt = s.booking.one.f_info
        x += image.width + mrgn
        x = W_PANEL - width_in_pixels(fnt, txt) - mrgn
        y = h_header + y_font_offset(fnt) + mrgn
        draw_text(cnv, x, y, txt, fnt, s.booking.c_timebox_free)

def _draw_header(cnv, court, s: ClubStyle):
    """Retuns the y coordinate (height) of the header section"""        
    f_name = s.booking.one.f_courtname
    
    mrgn = 2
    _y = y_font_offset(f_name) + mrgn        
    y_separator = _y + mrgn
    fill_rect(cnv, 0, 0, W_PANEL, y_separator, s.ci.c_bg_1)

    w_court_name = W_PANEL - mrgn*2
    
    txt = ellipsize(court['name'], f_name, w_court_name)

    _x = max(0 + mrgn, W_PANEL - width_in_pixels(f_name, txt) - mrgn)
    if txt != court['name']:
        # ellipsize
        txt = txt[:len(txt)-1] + SYMBOL_ELLIPSIS
    draw_text(cnv, _x, _y, txt, f_name, s.ci.c_text)

    graphics.DrawLine(cnv, 0, y_separator, W_PANEL, y_separator, s.ci.c_bg_2)

    return y_separator + 1

def _draw_time_box(cnv, y0, s: ClubStyle, color, txt_1:str, txt_2:str=None, txt_3:str=None):
    '''Return the width of the timebox component'''

    font = s.booking.one.f_timebox
    padding = 1
    mrgn = 2
    x = mrgn
    y = y0 + mrgn
    h = H_PANEL - y0 - mrgn - mrgn
    w = max(h, width_in_pixels(font, txt_1), width_in_pixels(font, txt_2), width_in_pixels(font, txt_3)) + padding
    draw_rect(cnv, x, y, w, h, s.ci.c_bg_1, round_corners=True)
    
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

        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, color)
        draw_text(cnv, x_txt_2, y_txt_2, txt_2, font, color)
        draw_text(cnv, x_txt_3, y_txt_3, txt_3, font, color)
    
    elif txt_2:
        h_txt = int(h_ / 2)
        y_delta_txt = y_font_center(font, h_txt)
        x_txt_1 = x + padding + x_font_center(txt_1, w_, font)
        x_txt_2 = x + padding + x_font_center(txt_2, w_, font)
        y_txt_1 = y + padding * 2 + y_delta_txt
        y_txt_2 = y - padding * 2 + y_delta_txt + h_txt
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, color)
        draw_text(cnv, x_txt_2, y_txt_2, txt_2, font, color)    
    elif txt_1:
        h_txt = int(h_ / 1)
        y_delta_txt = y_font_center(font, h_txt)
        x_txt_1 = x + padding + x_font_center(txt_1, w_, font)
        y_txt_1 = y + padding + y_delta_txt
        draw_text(cnv, x_txt_1, y_txt_1, txt_1, font, color)

    return w

def _draw_booking_match(cnv, s: ClubStyle, x0: int, y0: int, booking, footer=''):
    
    f_info = s.booking.one.f_info
    c_info = s.ci.c_text

    f_footer = s.booking.one.f_footer
    c_footer = s.booking.one.c_footer
    
    x = x0 + 2
    w = W_PANEL - x
    h = H_PANEL - y0 - 1
    w_row = w - 5
    h_row = int(h/3)
    
    # info (up to 2 lines)
    (txt_info_1, txt_info_2) = booking_info_texts(booking, w_row, f_info)
    if txt_info_1:
        if txt_info_2:
            _y = y0 + y_font_center(f_footer, h_row)
            draw_text(cnv, x, _y, txt_info_1, f_info, c_info)
            _y = y0 + h_row + y_font_center(f_footer, h_row)
            draw_text(cnv, x, _y, txt_info_2, f_info, c_info)
        else:
            _y = y0 + y_font_center(f_info, h_row)
            draw_text(cnv, x, _y, txt_info_1, f_info, c_info)

    # footer
    if footer:
        _y = y0 + 3 * h_row
        footer = ellipsize_text(footer, max_string_length_for_font(f_footer, w_row))
        draw_text(cnv, x, _y, footer, f_footer, c_footer)        