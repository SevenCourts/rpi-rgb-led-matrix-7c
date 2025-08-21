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
    
    # flags
    is_weather_displayed: bool = True
    is_court_name_acronym: bool = False
    is_club_area_left: bool = False

    # styles: colors and fonts
    c_free_to_book: graphics.Color = COLOR_7C_GREEN

    c_time_box_default: graphics.Color = COLOR_GREY
    c_time_box_countdown: graphics.Color = COLOR_7C_GOLD
    
    c_weather: graphics.Color = COLOR_WHITE
    f_weather: graphics.Font = FONT_M_SDK
    
    c_clock: graphics.Color = COLOR_WHITE
    f_clock: graphics.Font = FONT_L
    f_single_clock: graphics.Font = FONT_M
    
    f_court_name: graphics.Font = FONT_M
    f_single_court_name: graphics.Font = FONT_S
    
    c_info_text: graphics.Color = COLOR_WHITE
    f_info_text: graphics.Font = FONT_XS
    f_single_info_text: graphics.Font = FONT_M
    c_single_info_caption: graphics.Color = COLOR_GREY
    f_single_info_caption: graphics.Font = FONT_M

    f_time_box: graphics.Font = FONT_XXS
    f_single_time_box: graphics.Font = FONT_M

    c_separator: graphics.Color = COLOR_GREY_DARKEST
    

@dataclass
class ClubStyle:
    logo: LogoStyle = LogoStyle()
    ci: ClubCI = ClubCI()
    bookings: BookingStyle = BookingStyle()



# TABB Böblingen
COLOR_CI_TABB_1 = graphics.Color( int('0x29', 0), int('0x49', 0), int('0x75', 0))
COLOR_CI_TABB_2 = COLOR_GREY_DARK
style_TABB = ClubStyle(
    logo=LogoStyle(path='images/logos/TABB/tabb-logo-transparent-60x13-border-3.png'),
    ci=ClubCI(color_1=COLOR_CI_TABB_1, color_2=COLOR_CI_TABB_2),
    bookings=BookingStyle(is_weather_displayed=True, is_court_name_acronym=False)
)

# SV1845 Esslingen
COLOR_CI_SV1845_1 = graphics.Color( int('0x29', 0), int('0x49', 0), int('0x75', 0)) # Blue
COLOR_CI_SV1845_2 = graphics.Color( int('0xC9', 0), int('0x42', 0), int('0x40', 0)) # Red 
style_SV1845 = ClubStyle(
    logo=LogoStyle(path='images/logos/SV1845/sv1845_76x64_eBusy_demo_logo.png', round_corners=True),
    ci=ClubCI(color_1=COLOR_CI_SV1845_1, color_2=COLOR_CI_SV1845_2),
    bookings=BookingStyle(is_weather_displayed=False, is_court_name_acronym=True)
)

# Matchcenter Filderstadt
COLOR_CI_Matchcenter_1 = COLOR_GREY_DARKEST # Black
COLOR_CI_Matchcenter_2 = graphics.Color( int('0xE5', 0), int('0x00', 0), int('0x7D', 0)) # Magenta
style_MatchCenter = ClubStyle(
    logo=LogoStyle(path='images/logos/MatchCenter Filderstadt/logo-matchcenter_58x42.png'),
    ci=ClubCI(color_1=COLOR_CI_Matchcenter_1, color_2=COLOR_CI_Matchcenter_2),
    bookings=BookingStyle(is_weather_displayed=False, is_court_name_acronym=True)
)

