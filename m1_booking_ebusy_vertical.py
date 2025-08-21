from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import gettext
import m1_clock
import m1_image
from m1_booking_utils import *
from m1_club_styles import *

def _booking_height(courts_count:int = 3):
    switcher = {
        2: int(H_PANEL / 2), # 32
        3: int(H_PANEL / 3), # 21
        4: int(H_PANEL / 4), # 16
    }
    return switcher.get(courts_count, int(H_PANEL / 3))

def draw(cnv, booking_info, weather_info, panel_tz, s: ClubStyle):

    # Use datetime set in the Panel Admin UI for easier testing/debugging:
    _dev_timestamp = booking_info.get('_dev_timestamp')
    if _dev_timestamp and len(_dev_timestamp):
        time_now = parser.parse(_dev_timestamp)
    else:
        time_now = datetime.now(tz.gettz(panel_tz))

    # heights and widths
    w_clock = w_logo = width_in_pixels(s.bookings.f_clock, "00:00")    

    if s.bookings.is_club_area_left:
        x_clubarea = 0
        x_courts = w_clock + 2
    else:
        x_clubarea = W_PANEL - w_clock
        x_courts = 0
     
    _draw_club_area(cnv, x_clubarea, 0, w_clock, panel_tz, s, time_now, weather_info)

    ## booking infos
    h_booking = _booking_height(len(booking_info.get('courts')))
    w_booking = W_PANEL - max(w_clock, w_logo)
    y_court = 0
    for b in booking_info['courts']:

        last_row = (b == booking_info['courts'][-1])

        _draw_booking_court(cnv, x_courts, y_court, h_booking, w_booking, b, time_now, s, last_row)
        y_court += h_booking

def _draw_club_area(cnv, x0: int, y0: int, w: int, panel_tz, s: ClubStyle, time_now, weather_info):

    # weather
    f_weather = s.bookings.f_weather
    c_weather = s.bookings.c_weather
    h_weather = 0
    if weather_info and s.bookings.is_weather_displayed:
        temperature = f" {weather_info.get('temperature')}°"
        x_weather = x0 + x_font_center(temperature, w, f_weather)

        h_weather = y_font_offset(f_weather) + 2
        y_weather = y0 + h_weather
        graphics.DrawText(cnv, f_weather, x_weather, y_weather, c_weather, temperature)        

    # clock
    f_clock = s.bookings.f_clock
    c_clock = s.bookings.c_clock
    x_clock = x0
    h_clock = y_font_offset(f_clock) + 1
    y_clock = H_PANEL - 1
    m1_clock.draw_clock_by_coordinates(cnv, x_clock, y_clock, f_clock, panel_tz, c_clock, time_now)
    
    if s.ci.logo.path:
        ## logo
        h_logo_max = H_PANEL - h_clock - h_weather - 6
        img_logo = Image.open(s.ci.logo.path)
        m1_image.thumbnail(img_logo, w, min(h_logo_max, img_logo.height))
        h_logo = img_logo.height
        w_logo = img_logo.width
        x_logo_img = x0 + int((w - w_logo)/2)
        y_logo_img = h_weather + int((H_PANEL - h_clock - h_weather - h_logo) / 2)        
        cnv.SetImage(img_logo.convert('RGB'), x_logo_img, y_logo_img)

        if s.ci.logo.round_corners:
            round_rect_corners(cnv, x_logo_img, y_logo_img, img_logo.width, img_logo.height)
        ### logo placeholder bg
        #fill_rect(cnv, x_logo, y_logo, w_logo, h_logo, c_CI_primary)

    # vertical line separating club area and bookings area
    #if not s.bookings.is_club_area_left:
    #    graphics.DrawLine(cnv, x0, 0, x0, H_PANEL, s.ci.color_2)


def _draw_booking_court(cnv, x0: int, y0: int, h: int, w:int, court_bookings, time_now, s: ClubStyle, last_row: bool):

    w_court = 27 # TODO dynamic?
    w_time_left = w_court
    w_info_text = w - w_court - w_time_left - 2 - 2

    # court name
    max_length_court_name = 3 # TODO dynamic? style parameter?
    court_name = court_bookings['court']['name']
    if s.bookings.is_court_name_acronym:
        txt_court = ''.join(word[0].upper() for word in court_name.split() if word)        
    else:
        txt_court = court_name
    
    txt_court = txt_court[:max_length_court_name]

    _fnt = s.bookings.f_court_name
    x_court = x0
    y = y0 + 1
    h_court_name = h - 2
    fill_rect(cnv, x_court, y, w_court, h_court_name, s.ci.color_1, round_corners=True)
    #short line under court name
    #graphics.DrawLine(cnv, x_court + 1, y + h_court_name -1, x_court + w_court - 2, y + h_court_name - 1, s.ci.color_2)
    graphics.DrawLine(cnv, x_court + 2, y + h_court_name, x_court + w_court - 3, y + h_court_name, s.ci.color_2)
    #long line under whole booking
    if not last_row:
        graphics.DrawLine(cnv, x_court + w_court + 2, y + h_court_name, x0 + w - 2, y + h_court_name, s.bookings.c_separator)
    _x = x_court + x_font_center(txt_court, w_court + 2, _fnt)
    y += y_font_center(_fnt, h_court_name)
    graphics.DrawText(cnv, _fnt, _x, y, s.ci.color_font, txt_court)

    # Booking info (up to 2 rows)
    txt_info_1 = txt_info_2 = txt_status = ''
    
    b_1_current = court_bookings['current']
    b_2_next = court_bookings['next']

    booking = None
    
    c_time_left = s.bookings.c_time_box_default
    c_time_box_border = s.ci.color_1

    if b_1_current:

        t_start = parser.parse(b_1_current['start-date'])
        t_end = parser.parse(b_1_current['end-date'])

        t_0_upcoming_start = (t_start + TD_0_UPCOMING)
        t_3_countdown_start = (t_end + TD_3_COUNTDOWN)

        booking = b_1_current
        
        if time_now > t_0_upcoming_start:
            
            seconds_left = (t_end - time_now).seconds
            minutes_in_hour_left = seconds_left // 60 % 60 + 1
            hours_left = seconds_left // (60 * 60)

            if hours_left > 0:
                # default
                txt_status = f"> {hours_left} h"
            elif time_now < t_3_countdown_start:
                # default
                if minutes_in_hour_left < 10:
                    txt_status = f"{minutes_in_hour_left} min"
                else:
                    txt_status = f"{minutes_in_hour_left} m."                    
            elif time_now < t_end:
                # countdown                
                
                # Adjacent bookings handling: interchange every 10 seconds
                if b_2_next and is_current_second_in_period(PERIOD_INTERCHANGE_ADJACENT_S, time_now):
                    # show next
                    booking = b_2_next
                    t_start = parser.parse(booking['start-date'])
                    txt_status = f"{t_start.hour:02d}:{t_start.minute:02d}"
                else:
                    # show current
                    txt_status = f"{minutes_in_hour_left} min"
                    c_time_left = s.bookings.c_time_box_countdown
            else:
                raise ValueError('should never happen with eBusy data')
        else:
            raise ValueError('should never happen with eBusy data')
        
        (txt_info_1, txt_info_2) = booking_info_texts(booking, w_info_text, s.bookings.f_info_text)

    elif b_2_next:

        booking = b_2_next
        (txt_info_1, txt_info_2) = booking_info_texts(booking, w_info_text, s.bookings.f_info_text)
        t_start = parser.parse(booking['start-date'])
        txt_status = f"{t_start.hour}:{t_start.minute}"

    else:
        # no bookings - free
        c_time_left = s.bookings.c_free_to_book
        c_time_box_border = COLOR_BLACK
        txt_status = "Free"

    # TODO no need for border?
    c_time_box_border = COLOR_BLACK
    
    ## time box frame
    _fnt = s.bookings.f_time_box
    _h = h - 2
    x_time_left = x_court + w_court + 1
    _y = y0 + 1
    draw_rect(cnv, x_time_left, _y, w_time_left, _h, c_time_box_border, w_border=1, round_corners=True)
    
    ## sec info text
    _x = x_time_left + x_font_center(txt_status, w_time_left, _fnt) + 1
    _y += y_font_center(_fnt, _h)
    graphics.DrawText(cnv, _fnt, _x, _y, c_time_left, txt_status)
    
    # info
    x = x_time_left + w_time_left + 1
    if txt_info_1:
        c = s.bookings.c_info_text
        _fnt = s.bookings.f_info_text
        if txt_info_2:
            # correction for 4 courts rendering:
            is_enough_place_for_2_lines = h_court_name > (2 * (1 + y_font_offset(_fnt)))
            _y = y0 + int(h/2) - (0 if is_enough_place_for_2_lines else 1)
            graphics.DrawText(cnv, _fnt, x, _y, c, txt_info_1)
            _y += y_font_offset(_fnt) + 2 - (0 if is_enough_place_for_2_lines else 1)
            graphics.DrawText(cnv, _fnt, x, _y, c, txt_info_2)
        else:
            _y = y0 + y_font_center(_fnt, h)
            graphics.DrawText(cnv, _fnt, x, _y, c, txt_info_1)

    return