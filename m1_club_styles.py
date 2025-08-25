from sevencourts import *

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class LogoStyle:
    path: str = None
    round_corners: bool = False

@dataclass
class ClubCI:
    color_1: graphics.Color = COLOR_7C_BLUE_DARK
    color_2: graphics.Color = COLOR_7C_GREEN_DARK
    color_font: graphics.Color = COLOR_WHITE    
    logo: LogoStyle = LogoStyle()

@dataclass
class BookingStyle:
    
    # signange: 2 or 3 or 4 courts
    is_weather_displayed: bool = True
    is_court_name_acronym: bool = False
    is_club_area_left: bool = False

    court_name_truncate_to: int = 2

    c_weather: graphics.Color = COLOR_WHITE
    f_weather: graphics.Font = FONT_M_SDK
    
    c_clock: graphics.Color = COLOR_WHITE
    f_clock: graphics.Font = FONT_L
    f_single_clock: graphics.Font = FONT_M
    
    f_court_name: graphics.Font = FONT_M

    c_infotext: graphics.Color = COLOR_GREY
    f_infotext: Dict[int, tuple[graphics.Font]] = field(default_factory=lambda: {
        # number_of_courts : [font_for_1_row, font_for_2_rows]
        2: [FONT_S, FONT_S],
        3: [FONT_S, FONT_S],
        4: [FONT_S, FONT_XS]
    })

    c_timebox: graphics.Color = COLOR_WHITE
    c_timebox_countdown: graphics.Color = COLOR_7C_GOLD
    f_timebox: graphics.Font = FONT_S
    f_timebox_countdown: graphics.Font = FONT_M # TODO decide: same font size?

    c_timebox_border: graphics.Color = COLOR_BLACK
    c_timebox_border_free: graphics.Color = COLOR_BLACK
    c_timebox_free: graphics.Color = COLOR_7C_GREEN
    

    # single court
    f_time_box_single: graphics.Font = FONT_M
    f_courtname_single: graphics.Font = FONT_S

    f_info_text_single: graphics.Font = FONT_M
    c_info_caption_single: graphics.Color = COLOR_GREY
    f_info_caption_single: graphics.Font = FONT_M

    c_separator: graphics.Color = COLOR_GREY_DARKEST
    

@dataclass
class ClubStyle:
    ci: ClubCI = ClubCI()
    bookings: BookingStyle = BookingStyle()



# TABB Böblingen
COLOR_CI_TABB_1 = graphics.Color( int('0x29', 0), int('0x49', 0), int('0x75', 0))
COLOR_CI_TABB_2 = COLOR_GREY_DARK
style_TABB = ClubStyle(
    ci=ClubCI(color_1=COLOR_CI_TABB_1, color_2=COLOR_CI_TABB_2,
              logo=LogoStyle(path='images/logos/TABB/tabb-logo-transparent-60x13-border-3.png')),
    bookings=BookingStyle(is_weather_displayed=True, is_court_name_acronym=False)
)

# SV1845 Esslingen
COLOR_CI_SV1845_1 = graphics.Color( int('0x29', 0), int('0x49', 0), int('0x75', 0)) # Blue
COLOR_CI_SV1845_2 = graphics.Color( int('0xC9', 0), int('0x42', 0), int('0x40', 0)) # Red 
style_SV1845 = ClubStyle(
    ci=ClubCI(color_1=COLOR_CI_SV1845_1, color_2=COLOR_CI_SV1845_2,
              logo=LogoStyle(path='images/logos/SV1845/sv1845_76x64_eBusy_demo_logo.png', round_corners=True)),
    bookings=BookingStyle(is_weather_displayed=False, is_court_name_acronym=True)
)

# Matchcenter Filderstadt
COLOR_CI_Matchcenter_1 = COLOR_GREY_DARKEST # Black
COLOR_CI_Matchcenter_2 = graphics.Color( int('0xE5', 0), int('0x00', 0), int('0x7D', 0)) # Magenta
style_MatchCenter = ClubStyle(
    ci=ClubCI(color_1=COLOR_CI_Matchcenter_1, color_2=COLOR_CI_Matchcenter_2,
              logo=LogoStyle(path='images/logos/MatchCenter Filderstadt/logo-matchcenter_58x39.png')),
    bookings=BookingStyle(is_weather_displayed=False, is_court_name_acronym=True)
)

# SevenCourts
COLOR_CI_SevenCourts_1 = COLOR_7C_BLUE_DARK
COLOR_CI_SevenCourts_2 = COLOR_7C_GREEN_DARK
style_SevenCourts = ClubStyle(
    ci=ClubCI(color_1=COLOR_CI_SevenCourts_1, color_2=COLOR_CI_SevenCourts_2,
              logo=LogoStyle(path='images/logos/SevenCourts/sevencourts_58x6.png')),
    bookings=BookingStyle(is_weather_displayed=True, is_court_name_acronym=True)
)

