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
        
    # Use datetime set in the Panel Admin UI for easier testing/debugging:
    _dev_timestamp = booking_info.get('_dev_timestamp')
    if _dev_timestamp and len(_dev_timestamp):
        time_now = parser.parse(_dev_timestamp)
    else:
        time_now = datetime.now(tz.gettz(panel_tz))

    # do not show time if no booking to show (time will be displayed in the main area)
    show_time_in_header = b_0_past or b_1_current or b_2_next
    h_header = _draw_header(cnv, court, s, time_now if show_time_in_header else None)


    c_timebox_warn = s.bookings.c_time_box_countdown
    c_timebox = s.bookings.c_time_box_default

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
        # no bookings - show a default
        image = Image.open(s.ci.logo.path)
        MAX_IMAGE_WIDTH = 76 # so that 22:22 time fits
        h_logo = H_PANEL - h_header - mrgn
        m1_image.thumbnail(image, MAX_IMAGE_WIDTH, h_logo)
        x = 0
        y = h_header + (h_logo - image.height) // 2 + 1
        cnv.SetImage(image.convert('RGB'), x, y)
        if s.ci.logo.round_corners:
            round_rect_corners(cnv, x, y, image.width, image.height)

        txt_time = time_now.strftime('%H:%M')
        fnt = m1_clock.FONT_CLOCK_M_1
        x += image.width + mrgn
        x = x + x_font_center(txt_time, W_PANEL - x, fnt)
        y = h_header + y_font_center(fnt, H_PANEL - h_header)
        draw_text(cnv, x, y, txt_time, fnt, s.ci.color_font)

def _draw_header(cnv, court, s: ClubStyle, dt=None):
    """Retuns the y coordinate (height) of the header section"""        
    f_name = s.bookings.f_single_court_name
    f_time = s.bookings.f_single_clock

    mrgn = 2
    x_court_name = 0 + mrgn
    y_court_name = y_font_offset(f_name) + mrgn
        
    if dt:
        txt_clock = dt.strftime('%H:%M') # FIXME WTF
        x_clock = W_PANEL - mrgn - width_in_pixels(f_time, txt_clock)    
        y_clock =  y_font_offset(f_time) + mrgn        
        y_separator = max(y_clock, y_court_name) + mrgn                
    else:
        y_separator = y_court_name + mrgn

    fill_rect(cnv, 0, 0, W_PANEL, y_separator, s.ci.color_1)

    if dt:
        draw_text(cnv, x_clock, y_clock, txt_clock, f_time, s.ci.color_font)
        w_clock = width_in_pixels(f_name, txt_clock)
    else:
        w_clock = 0    
    w_court_name = W_PANEL - w_clock - mrgn*2
    txt_court_name = truncate_text(f_name, w_court_name, court['name'])
    if txt_court_name != court['name']:
        # ellipsize
        txt_court_name = txt_court_name[:len(txt_court_name)-4] + "..."
    draw_text(cnv, x_court_name, y_court_name, txt_court_name, f_name, s.ci.color_font)


    graphics.DrawLine(cnv, 0, y_separator, W_PANEL, y_separator, s.ci.color_2)

    return y_separator + 1

def _draw_time_box(cnv, y0, s: ClubStyle, color, txt_1:str, txt_2:str=None, txt_3:str=None):
    '''Return the width of the timebox component'''

    font = s.bookings.f_single_time_box    
    padding = 1
    mrgn = 2
    x = mrgn
    y = y0 + mrgn
    h = H_PANEL - y0 - mrgn - mrgn
    w = max(h, width_in_pixels(font, txt_1), width_in_pixels(font, txt_2), width_in_pixels(font, txt_3)) + padding
    draw_rect(cnv, x, y, w, h, s.ci.color_1, round_corners=True)
    
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

def _draw_booking_match(cnv, s: ClubStyle, x0: int, y0: int, booking, caption=''):
    
    f_caption = s.bookings.f_single_info_caption
    c_caption = s.bookings.c_single_info_caption

    f_info = s.bookings.f_single_info_text
    c_info = s.bookings.c_info_text
    

    x = x0 + 2
    y = y0
    w = W_PANEL - x
    h = H_PANEL - y - 1
    w_text = w - 5
    
    # caption
    if caption:
        h_row = int(h/3)
        y_txt = y + y_font_center(f_caption, h_row)
        caption = ellipsize(caption, max_string_length_for_font(f_caption, w_text))
        draw_text(cnv, x, y_txt, caption, f_caption, c_caption)        
        y += h_row
    else:
        h_row = int(h/2)
        
    # info (up to 2 lines)
    (txt_info_1, txt_info_2) = booking_info_texts(booking, w_text, f_info)
    if txt_info_1:
        if txt_info_2:
            y_txt = y + y_font_center(f_caption, h_row)
            draw_text(cnv, x, y_txt, txt_info_1, f_info, c_info)
            y_txt = y + h_row + y_font_center(f_caption, h_row)
            draw_text(cnv, x, y_txt, txt_info_2, f_info, c_info)            
        else:
            y_txt = y + y_font_center(f_info, h)
            draw_text(cnv, x, y_txt, txt_info_1, f_info, c_info)
