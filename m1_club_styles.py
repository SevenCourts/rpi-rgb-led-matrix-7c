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
    c_free_to_book: graphics.Color = COLOR_GREEN

    c_time_box_default: graphics.Color = COLOR_GREY
    c_time_box_countdown: graphics.Color = COLOR_GOLD
    
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
    

@dataclass
class ClubStyle:
    logo: LogoStyle = LogoStyle()
    ci: ClubCI = ClubCI()
    bookings: BookingStyle = BookingStyle()