from sevencourts import *

from dateutil import parser, tz
from datetime import datetime, timedelta
import gettext
import requests
import m1_clock
import m1_image

from dataclasses import dataclass

@dataclass
class ClubStyle:
    path_logo: str = None
    color_CI: graphics.Color = COLOR_7C_BLUE_DARK
    color_font: graphics.Color = COLOR_WHITE
    is_weather_displayed: bool = True
    is_court_name_acronym: bool = False


logger = m1_logging.logger("eBusy")

# Style sheet
FONT_COURT_NAME = FONT_S
FONT_CURRENT_TIME = FONT_S
FONT_TIME_BOX = FONT_M
FONT_BOOKING_CAPTION = FONT_S
FONT_BOOKING_NAME = FONT_M
FONT_MESSAGE = FONT_M

COLOR_HEADER_BG = COLOR_CI_SV1845

COLOR_COURT_NAME = COLOR_WHITE
COLOR_CURRENT_TIME = COLOR_WHITE

COLOR_TIME_BOX = COLOR_WHITE
COLOR_TIME_BOX_BG_INFO = COLOR_CI_SV1845
COLOR_TIME_BOX_BG_WARN = COLOR_7C_RED

COLOR_BOOKING = COLOR_WHITE
COLOR_MESSAGE = COLOR_YELLOW

COLOR_SEPARATOR_LINE = COLOR_GREY_DARK

MARGIN = 2
H_HEADER = 12

TD_0_UPCOMING = timedelta(minutes = -5)
TD_1_WELCOME = timedelta(minutes = 2)
TD_3_COUNTDOWN = TD_0_UPCOMING # these two should be equal
TD_4_GAMEOVER = timedelta(minutes = 2)

def _booking_player(player):
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
                txt = _('booking.guest')
        return txt

def booking_team(booking, isTeam1=True):
    txt = None
    tp1 =  booking['p1'] if isTeam1 else booking.get('p3')
    if tp1:
        txt = _booking_player(tp1)
    tp2 =  booking['p2'] if isTeam1 else booking.get('p4')
    if tp2:
        if txt:
            txt += ', '
        txt = (txt or '') + _booking_player(tp2)
    return txt