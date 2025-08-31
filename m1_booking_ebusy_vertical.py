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
        1: (H_PANEL // 1, 4), # 64
        2: (H_PANEL // 2, 3), # 32
        3: (H_PANEL // 3, 1), # 21
        4: (H_PANEL // 4, 0), # 16
    }
    return switcher.get(courts_count, H_PANEL // 3)

def draw(cnv, booking_info, weather_info, panel_tz, s: ClubStyle):

    # Use datetime set in the Panel Admin UI for easier testing/debugging:
    _dev_timestamp = booking_info.get('_dev_timestamp')
    if _dev_timestamp and len(_dev_timestamp):
        time_now = parser.parse(_dev_timestamp)
    else:
        time_now = datetime.now(tz.gettz(panel_tz))

    # heights and widths
    w_clock = w_logo = width_in_pixels(s.booking.f_clock, "00:00") - 2 # px to the right are empty

    x_clubarea = W_PANEL - w_clock
    x_courts = 0
    
    if False:
        #texgyre27 font
        _w = 15 + 15 + 7 + 15 + 15 # 67
        _h = 20
        draw_rect(cnv, W_PANEL - _w, H_PANEL - _h, _w, _h, COLOR_MAGENTA)

    _draw_club_area(cnv, x_clubarea, 0, w_clock, panel_tz, s, time_now, weather_info)

    ## booking infos
    courts_number = len(booking_info.get('courts'))
    (h_booking, rows_spacing) = _booking_height(courts_number)
    w_booking = W_PANEL - max(w_clock, w_logo)
    y_court = 0
    for b in booking_info['courts']:

        last_row = (b == booking_info['courts'][-1])

        _draw_booking_court(cnv, x_courts, y_court, w_booking,h_booking, rows_spacing, b, time_now, s, courts_number, last_row)
        y_court += h_booking
    

def _draw_club_area(cnv, x0: int, y0: int, w: int, panel_tz, s: ClubStyle, time_now, weather_info):

    # weather
    f_weather = s.booking.many.f_weather
    c_weather = s.booking.many.c_weather
    h_weather = 0
    if weather_info and s.booking.is_weather_displayed:
        temperature = f" {weather_info.get('temperature')}°"
        x_weather = x0 + x_font_center(temperature, w, f_weather)

        h_weather = y_font_offset(f_weather) + 2
        y_weather = y0 + h_weather
        graphics.DrawText(cnv, f_weather, x_weather, y_weather, c_weather, temperature)        

    # clock
    f_clock = s.booking.f_clock
    c_clock = s.booking.c_clock
    x_clock = x0
    h_clock = y_font_offset(f_clock) + 1
    y_clock = H_PANEL
    m1_clock.draw_clock_by_coordinates(cnv, x_clock, y_clock, f_clock, panel_tz, c_clock, time_now)
    
    if s.ci.logo.path:
        ## logo
        h_logo_max = H_PANEL - h_clock - h_weather - 6
        img_logo = Image.open(s.ci.logo.path)
        m1_image.thumbnail(img_logo, w, min(h_logo_max, img_logo.height))
        h_logo = img_logo.height
        w_logo = img_logo.width
        x_logo_img = x0 + (w - w_logo) // 2
        y_logo_img = h_weather + (H_PANEL - h_clock - h_weather - h_logo) // 2
        cnv.SetImage(img_logo.convert('RGB'), x_logo_img, y_logo_img)

        if s.ci.logo.round_corners:
            round_rect_corners(cnv, x_logo_img, y_logo_img, img_logo.width, img_logo.height)
        ### logo placeholder bg
        #fill_rect(cnv, x_logo, y_logo, w_logo, h_logo, c_CI_primary)


def _draw_booking_court(cnv, x0: int, y0: int, w:int, h: int, rows_spacing: int, 
                        court_bookings, time_now, s: ClubStyle, courts_number: int, last_row: bool):
    
    if False:
        draw_rect(cnv, x0, y0, w, h, COLOR_MAGENTA)

    w_court = width_in_pixels(s.booking.many.f_court_name, "X" * s.booking.courtname_truncate_to) + 4
    w_timebox = width_in_pixels(s.booking.many.f_timebox, "22:22") + 2
    w_info = w - w_court - w_timebox - 4

    # court name    
    court_name = court_bookings['court']['name']

    court_name = court_name.replace("Platz", "Court") # FIXME demo only, remove ".replace"

    if s.booking.is_courtname_acronym:
        txt_court = acronym(court_name)
    else:
        txt_court = court_name
    txt_court = txt_court[:s.booking.courtname_truncate_to]

    _fnt = s.booking.many.f_court_name
    x_court = x0
    y = y0 + 1
    h_court_name = h - 2
    fill_rect(cnv, x_court, y, w_court, h_court_name, s.ci.c_bg_1, round_corners=True)
    #short line under court name
    #graphics.DrawLine(cnv, x_court + 1, y + h_court_name -1, x_court + w_court - 2, y + h_court_name - 1, s.ci.color_2)
    graphics.DrawLine(cnv, x_court + 2, y + h_court_name, x_court + w_court - 3, y + h_court_name, s.ci.c_bg_2)
    #long line under whole booking
    if not last_row:
        graphics.DrawLine(cnv, x_court + w_court + 2, y + h_court_name, x0 + w - 2, y + h_court_name, 
                          s.booking.many.c_separator)
    _x = x_court + x_font_center(txt_court, w_court + 2, _fnt)
    y += y_font_center(_fnt, h_court_name)
    graphics.DrawText(cnv, _fnt, _x, y, s.ci.c_text, txt_court)

    # Booking info (up to 2 rows)
    txt_info_1 = txt_info_2 = txt_status = ''
    
    b_1_current = court_bookings['current']
    b_2_next = court_bookings['next']

    booking = None
    
    c_timebox = s.booking.c_timebox
    f_timebox = s.booking.many.f_timebox
    c_timebox_border = s.booking.many.c_timebox_border

    if b_1_current:

        t_start = parser.parse(b_1_current['start-date'])
        t_end = parser.parse(b_1_current['end-date'])

        t_0_upcoming_start = (t_start + TD_0_UPCOMING)
        t_3_countdown_start = (t_end + TD_3_COUNTDOWN)

        booking = b_1_current
        
        if time_now > t_0_upcoming_start:

            (hours_left, minutes_in_hour_left) = hours_minutes_diff(t_end, time_now)

            if hours_left > 0:
                # default
                txt_status = f">{hours_left}h"
            elif time_now < t_3_countdown_start:
                # default
                txt_status = f" {minutes_in_hour_left}'"
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
                    txt_status = f"{minutes_in_hour_left}'"
                    c_timebox = s.booking.c_timebox_countdown
                    f_timebox = s.booking.many.f_timebox_countdown
            else:
                txt_status = f" {minutes_in_hour_left}'"                
                # raise ValueError('should never happen with eBusy data')
                '''
                For 2025-08-28T23:01:00

                
                2) start time of the next booking is the same as the end time of the current booking

                "current": {
                    "start-date": "2025-08-28T22:00"
                    "end-date": "2025-08-28T00:00"
                }

                start: 2025-08-28 22:00:00
                end:   2025-08-28 00:00:00 (!!)
                t0:   2025-08-28 21:55
                t1:   2025-08-28 22:02
                t3:   2025-08-27 23:55 (!!!)
                '''
        else:
            raise ValueError('should never happen with eBusy data')
        
        

    elif b_2_next:

        booking = b_2_next
        t_start = parser.parse(booking['start-date'])
        txt_status = f"{t_start.hour:02d}:{t_start.minute:02d}"

    else:
        # no bookings - free
        c_timebox = s.booking.c_free_to_book
        c_timebox_border = s.booking.many.c_timebox_border_free
        txt_status = 'Free'

    ((txt_info_1, txt_info_2), font) = booking_info_texts(booking, w_info, s.booking.many.f_infotext[courts_number])
    # draw

    ## time box frame
    _h = h - 2
    x_time_box = x_court + w_court + 1
    _y = y0 + 1
    draw_rect(cnv, x_time_box, _y, w_timebox, _h, c_timebox_border, w_border=1, round_corners=True)
        
    ## time box text
    _fnt = f_timebox
    _x = x_time_box + x_font_center(txt_status, w_timebox, _fnt)
    _y += y_font_center(_fnt, _h)
    graphics.DrawText(cnv, _fnt, _x, _y, c_timebox, txt_status)

    
    # info texts
    if txt_info_1:
        _c = s.booking.many.c_infotext
        _x = x_time_box + w_timebox + 2        
        if txt_info_2:
            _fnt = s.booking.many.f_infotext[courts_number][1]

            _y = y0 + h//2 - 2 + (1 if courts_number == 4 else 0)

            if False:
                draw_rect(cnv, _x, y0, w_info, h, COLOR_MAGENTA)

            graphics.DrawText(cnv, _fnt, _x, _y, _c, txt_info_1)
            _y += y_font_offset(_fnt) + 1 + rows_spacing
            graphics.DrawText(cnv, _fnt, _x, _y, _c, txt_info_2)
        else:
            _fnt = font
            _y = y0 + y_font_center(_fnt, h)
            if False:
                draw_rect(cnv, _x, y0, w_info, h, COLOR_MAGENTA)
            graphics.DrawText(cnv, _fnt, _x, _y, _c, txt_info_1)
    return