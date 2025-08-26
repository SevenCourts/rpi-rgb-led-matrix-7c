from sevencourts import *

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Logo:
    path: str = None
    round_corners: bool = False

@dataclass
class ClubCI:
    c_text: graphics.Color = COLOR_WHITE
    c_bg_1: graphics.Color = COLOR_7C_BLUE_DARK
    c_bg_2: graphics.Color = COLOR_7C_GREEN_DARK
    logo: Logo = Logo()

@dataclass
class SingleCourt:

    is_show_timebox_left: bool = True
    '''
    Timebox is displayed on the left if True.
    Timebox is displayed above the clock if False.
    '''

    f_info: graphics.Font = FONT_M
    c_footer: graphics.Color = COLOR_GREY_DARK
    f_footer: graphics.Font = FONT_S
    
    f_timebox: graphics.Font = FONT_M
    f_courtname: graphics.Font = FONT_S
    

@dataclass
class MultipleCourts:
    '''
    Signange: 2 or 3 or 4 courts.
    '''

    is_club_area_left: bool = False

    is_use_for_single_court: bool = False
    '''If to use signage mode also for a single court (1 row).'''

    courtname_truncate_to: int = 2

    c_weather: graphics.Color = COLOR_WHITE
    f_weather: graphics.Font = FONT_M_SDK
            
    f_court_name: graphics.Font = FONT_M

    c_infotext: graphics.Color = COLOR_GREY
    f_infotext: Dict[int, tuple[graphics.Font]] = field(default_factory=lambda: {
        # number_of_courts : [font_for_1_row, font_for_2_rows]
        2: [FONT_S, FONT_S],
        3: [FONT_S, FONT_S],
        4: [FONT_S, FONT_XS]
    })

    f_timebox: graphics.Font = FONT_S
    f_timebox_countdown: graphics.Font = FONT_S

    c_timebox_border: graphics.Color = COLOR_BLACK
    c_timebox_border_free: graphics.Color = COLOR_BLACK

    c_separator: graphics.Color = COLOR_GREY_DARKEST
    

@dataclass
class Booking:
    c_clock: graphics.Color = COLOR_WHITE
    f_clock: graphics.Font = FONT_L

    c_timebox: graphics.Color = COLOR_WHITE
    c_timebox_countdown: graphics.Color = COLOR_7C_GOLD
    c_timebox_free: graphics.Color = COLOR_7C_GREEN

    is_weather_displayed: bool = True
    is_courtname_acronym: bool = False

    one: SingleCourt = SingleCourt()
    many: MultipleCourts = MultipleCourts()
    

@dataclass
class ClubStyle:
    ci: ClubCI = ClubCI()
    booking: Booking = Booking()



# TABB Böblingen
COLOR_CI_TABB_1 = graphics.Color( int('0x29', 0), int('0x49', 0), int('0x75', 0))
COLOR_CI_TABB_2 = COLOR_GREY_DARK
style_TABB = ClubStyle(
    ci=ClubCI(c_bg_1=COLOR_CI_TABB_1, c_bg_2=COLOR_CI_TABB_2,
              logo=Logo(path='images/logos/TABB/tabb-logo-transparent-60x13-border-3.png')),
    booking=Booking(
        is_weather_displayed=True, 
        is_courtname_acronym=False,
        many=MultipleCourts(courtname_truncate_to=3)))

# SV1845 Esslingen
COLOR_CI_SV1845_1 = graphics.Color( int('0x29', 0), int('0x49', 0), int('0x75', 0)) # Blue
COLOR_CI_SV1845_2 = graphics.Color( int('0xC9', 0), int('0x42', 0), int('0x40', 0)) # Red 
style_SV1845 = ClubStyle(
    ci=ClubCI(c_bg_1=COLOR_CI_SV1845_1, c_bg_2=COLOR_CI_SV1845_2,
              logo=Logo(path='images/logos/SV1845/sv1845_76x64_eBusy_demo_logo.png', round_corners=True)),
    booking=Booking(is_weather_displayed=False, is_courtname_acronym=True))

# Matchcenter Filderstadt
COLOR_CI_Matchcenter_1 = COLOR_GREY_DARKEST # Black
COLOR_CI_Matchcenter_2 = graphics.Color( int('0xE5', 0), int('0x00', 0), int('0x7D', 0)) # Magenta
style_MatchCenter = ClubStyle(
    ci=ClubCI(c_bg_1=COLOR_CI_Matchcenter_1, c_bg_2=COLOR_CI_Matchcenter_2,
              logo=Logo(path='images/logos/MatchCenter Filderstadt/logo-matchcenter_58x39.png')),
    booking=Booking(is_weather_displayed=False, is_courtname_acronym=True)
)

# SevenCourts
COLOR_CI_SevenCourts_1 = COLOR_7C_BLUE_DARK
COLOR_CI_SevenCourts_2 = COLOR_7C_GREEN_DARK
style_SevenCourts = ClubStyle(
    ci=ClubCI(c_bg_1=COLOR_CI_SevenCourts_1, c_bg_2=COLOR_CI_SevenCourts_2,
              logo=Logo(path='images/logos/SevenCourts/sevencourts_58x6.png')),
    booking=Booking(is_weather_displayed=True, is_courtname_acronym=True)
)

