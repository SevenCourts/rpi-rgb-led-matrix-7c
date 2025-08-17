from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import gettext
import m1_clock
import m1_image
from m1_booking_utils import *

# fonts
f_clock = FONT_L
f_weather = FONT_M_SDK
f_booking_court = FONT_M
f_booking_info = FONT_XS
f_booking_status = FONT_XXS

# colors
## TABB
c_CI_pri = graphics.Color(5, 105, 167) # blue
c_CI_sec = COLOR_WHITE # white

c_grid = None # COLOR_7C_GOLD

c_clock = COLOR_WHITE
c_weather = COLOR_WHITE
c_clock_separator = COLOR_GREY_DARK
c_booking_court = c_CI_sec
c_booking_court_bg = c_CI_pri
c_booking_info = COLOR_WHITE
c_booking_status_default = COLOR_GREY
c_booking_status_free = COLOR_GREEN
c_booking_status_countdown = COLOR_7C_GOLD

def _booking_height(courts_count:int = 3):
    switcher = {
        2: int(H_PANEL / 2), # 32
        3: int(H_PANEL / 3), # 21
        4: int(H_PANEL / 4), # 16
    }
    return switcher.get(courts_count, int(H_PANEL / 3))

def draw(cnv, booking_info, weather_info, panel_tz):

    # Use datetime set in the Panel Admin UI for easier testing/debugging:
    _dev_timestamp = booking_info['_dev_timestamp']
    if _dev_timestamp and len(_dev_timestamp):
        time_now = parser.parse(_dev_timestamp)
    else:
        time_now = datetime.now(tz.gettz(panel_tz))

    total_courts = len(booking_info['courts'])

    # heights and widths
    w_clock = w_logo = width_in_pixels(f_clock, "00:00")    
    _draw_club_area(cnv, 0, 0, w_clock, panel_tz, 'images/logos/TABB/tabb-logo-transparent-60x13.png', time_now, weather_info)

    ## booking infos
    h_booking = _booking_height(total_courts)
    w_booking = W_PANEL - max(w_clock, w_logo)
    y = 0
    x = w_clock + 2
    for b in booking_info['courts']:
        _draw_booking_court(cnv, x, y, h_booking, w_booking, b, time_now)
        y += h_booking

def _draw_club_area(cnv, x0: int, y0: int, w: int, panel_tz, path_to_logo_image, time_now, weather_info):

    style = 'BigClock'
    style = 'WithLogo'

    if style == 'BigClock':
        x_clock = x0
        h_clock = y_font_offset(f_clock) + 1
        y_clock = 1 + h_clock
        m1_clock.draw_clock_by_coordinates(cnv, x_clock, y_clock, f_clock, panel_tz, c_clock, time_now)
    elif style == 'WithLogo':
        # clock
        x_clock = x0
        h_clock = y_font_offset(f_clock) + 1
        y_clock = 1 + h_clock
        m1_clock.draw_clock_by_coordinates(cnv, x_clock, y_clock, f_clock, panel_tz, c_clock, time_now)

        ## logo
        logo_img = Image.open(path_to_logo_image)
        m1_image.thumbnail(logo_img, w, logo_img.height)
        x_logo_img = x0
        y_logo_img = int((H_PANEL + logo_img.height) / 2) - logo_img.height
        cnv.SetImage(logo_img.convert('RGB'), x_logo_img, y_logo_img)
        #round_rect_corners(cnv, x_logo_img, y_logo_img, logo_img.width, logo_img.height)
        ### logo placeholder bg
        #fill_rect(cnv, x_logo, y_logo, w_logo, h_logo, c_CI_primary)

    # weather
    if weather_info:
        temperature = f"{weather_info.get('temperature')}°C"
        x_weather = x_font_center(temperature, w, f_weather)
        y_weather = H_PANEL - 2
        graphics.DrawText(cnv, f_weather, x_weather, y_weather, c_weather, temperature)


    if c_grid:
        ### vertical line separating clock
        graphics.DrawLine(cnv, x_clock, 0, x_clock, H_PANEL, c_grid)
        ### horizontal line separating clock and logo
        graphics.DrawLine(cnv, x_clock, y_clock, W_PANEL, y_clock, c_grid)
    # vertical line separating club area and bookings area
    #x = w
    #graphics.DrawLine(cnv, x, 0, x, H_PANEL, c_clock_separator)


def _draw_booking_court(cnv, x0: int, y0: int, h: int, w:int, court_bookings, time_now):

    court_name = court_bookings['court']['name']

    w_court_name = 25

    max_length_court_name = 3

    # court name
    txt = court_name[:max_length_court_name]
    fnt = f_booking_court
    x = x0
    y = y0 + 1
    _w = w_court_name
    h_court_name = h - 2
    fill_rect(cnv, x, y, _w, h_court_name, c_booking_court_bg, round_corners=True)
    x += x_font_center(txt, _w+2, fnt)
    y += y_font_center(fnt, h_court_name)
    graphics.DrawText(cnv, fnt, x, y, c_booking_court, txt)

    # Booking info (up to 2 rows)
    txt_info_row_1 = txt_info_row_2 = txt_status = ''
    
    b_1_current = court_bookings['current']
    b_2_next = court_bookings['next']

    booking = None
    
    c_status = c_booking_status_default

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
                
                # Adjacent bookings handling
                    #  0 - 14 show current
                    # 15 - 29 show next
                    # 30 - 44 show current
                    # 45 - 59 show next
                if b_2_next and (time_now.second >= 15 and time_now.second <= 29) or (time_now.second >= 45 and time_now.second <= 59):
                    # show next
                    booking = b_2_next
                    t_start = parser.parse(b_2_next['start-date'])
                    txt_status = f"{t_start.hour:02d}:{t_start.minute:02d}"
                else:
                    # show current
                    txt_status = f"{minutes_in_hour_left} min"
                    c_status = c_booking_status_countdown
            else:
                raise ValueError('should never happen with eBusy data')
        else:
            raise ValueError('should never happen with eBusy data')

        if booking['display-text']:
            w_info = w - w_court_name * 2 - 2            
            max_text_length = max_string_length_for_font(f_booking_info, w_info)
            for wrd in booking['display-text'].split():
                if txt_info_row_1:
                    if len(txt_info_row_1 + ' ' + wrd) <= max_text_length:
                        txt_info_row_1 += ' ' + wrd
                    else:
                        txt_info_row_2 += (' ' if txt_info_row_2 else '') + wrd
                else:
                    txt_info_row_1 = wrd
            if len(txt_info_row_2) > max_text_length:
                # ellipsize 2nd row            
                txt_info_row_2 = txt_info_row_2[:max_text_length]
        else:
            txt_info_row_1 = booking_team(booking, True)
            txt_info_row_2 = booking_team(booking, False)

    elif b_2_next:

        booking = b_2_next
        txt_info_row_1 = booking_team(booking, True)
        txt_info_row_2 = booking_team(booking, False)
        t_start = parser.parse(booking['start-date'])
        txt_status = f"{t_start.hour}:{t_start.minute}"

    else:
        # no bookings - free
        c_status = c_booking_status_free        
        txt_status = "Free"
    
    # secondary info
    ## sec info frame
    w_status = w_court_name
    _h = h - 2
    _x = W_PANEL - w_status
    _y = y0 + 1
    draw_rect(cnv, _x, _y, w_status, _h, c_booking_court_bg, w_border=1, color_fill=COLOR_BLACK, round_corners=True)
    ## sec info text
    _x += x_font_center(txt_status, w_status, f_booking_status) + 1
    _y += y_font_center(f_booking_status, _h)
    graphics.DrawText(cnv, f_booking_status, _x, _y, c_status, txt_status)
    
    # primary info
    _x = x0 + w_court_name + 1
    if txt_info_row_1:
        c = c_booking_info
        if txt_info_row_2:
            # correction for 4 courts rendering:
            is_enough_place_for_2_lines = h_court_name > (2 * (1 + y_font_offset(f_booking_info)))
            _y = y0 + int(h/2) - (0 if is_enough_place_for_2_lines else 1)
            graphics.DrawText(cnv, f_booking_info, _x, _y, c, txt_info_row_1)
            _y += y_font_offset(f_booking_info) + 2
            graphics.DrawText(cnv, f_booking_info, _x, _y, c, txt_info_row_2)
        else:
            _y = y0 + y_font_center(f_booking_info, h)
            graphics.DrawText(cnv, f_booking_info, _x, _y, c, txt_info_row_1)

    if c_grid:
        ### vertical line separating booking court from info
        graphics.DrawLine(cnv, w_court_name, 0, w_court_name, H_PANEL, c_grid)
        ### horizontal line between bookings
        graphics.DrawLine(cnv, x0, y0 + h, x0 + w, y0 + h, c_grid)

    return