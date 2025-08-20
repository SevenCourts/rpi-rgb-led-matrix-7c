from sevencourts import *

from dataclasses import dataclass

@dataclass
class LogoStyle:
    path: str = None
    round_corners: bool = False

@dataclass
class ClubCI:
    color_1: graphics.Color = COLOR_7C_BLUE_DARK
    color_2: graphics.Color = COLOR_7C_GREEN_DARK
    color_font: graphics.Color = COLOR_WHITE    

@dataclass
class BookingStyle:
    is_weather_displayed: bool = True
    is_court_name_acronym: bool = False
    is_club_area_left: bool = False

@dataclass
class ClubStyle:
    logo: LogoStyle = LogoStyle()
    ci: ClubCI = ClubCI()
    bookings: BookingStyle = BookingStyle()

# Style sheet
FONT_COURT_NAME = FONT_S
FONT_CURRENT_TIME = FONT_S
FONT_TIME_BOX = FONT_M
FONT_BOOKING_CAPTION = FONT_S
FONT_BOOKING_NAME = FONT_M
FONT_MESSAGE = FONT_M

COLOR_HEADER_BG = COLOR_CI_SV1845_1

COLOR_COURT_NAME = COLOR_WHITE
COLOR_CURRENT_TIME = COLOR_WHITE

COLOR_TIME_BOX = COLOR_WHITE
COLOR_TIME_BOX_BG_INFO = COLOR_CI_SV1845_1
COLOR_TIME_BOX_BG_WARN = COLOR_7C_RED

COLOR_BOOKING = COLOR_WHITE
COLOR_MESSAGE = COLOR_YELLOW

COLOR_SEPARATOR_LINE = COLOR_GREY_DARK

MARGIN = 2
H_HEADER = 12