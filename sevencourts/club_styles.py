from sevencourts.rgbmatrix import *
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Logo:
    path: str = None
    round_corners: bool = False


@dataclass
class ClubCI:
    c_text: graphics.Color = COLOR_WHITE
    c_bg_1: graphics.Color = COLOR_7C_DARK_BLUE
    c_bg_2: graphics.Color = COLOR_7C_DARK_GREEN
    logo: Logo = Logo()


@dataclass
class OneCourt:
    """
    Timebox is displayed on the left if True.
    Timebox is displayed above the clock if False.
    """

    is_court_name_on_top: bool = True
    """Otherwise the court name will be displayed on the left"""

    f_info: graphics.Font = FONT_M
    c_prompt: graphics.Color = COLOR_7C_GOLD
    f_prompt: graphics.Font = FONT_S

    f_timebox: graphics.Font = FONT_M
    f_courtname_on_top: graphics.Font = FONT_S
    f_courtname_on_left: graphics.Font = FONT_M


@dataclass
class MultipleCourts:
    """
    Signange: 2 or 3 or 4 courts.
    """

    c_weather: graphics.Color = COLOR_WHITE
    f_weather: graphics.Font = FONT_M_SDK

    f_court_name: graphics.Font = FONT_M

    c_infotext: graphics.Color = COLOR_GREY
    f_infotext: Dict[int, tuple[graphics.Font]] = field(
        default_factory=lambda: {
            # number_of_courts : [font_for_1_(one)_row, font_for_2_rows]
            1: [FONT_L, FONT_M],
            2: [FONT_S, FONT_S],
            3: [FONT_S, FONT_S],
            4: [FONT_S, FONT_XS],
        }
    )

    f_timebox: graphics.Font = FONT_S
    f_timebox_countdown: graphics.Font = FONT_S

    c_timebox_border: graphics.Color = COLOR_BLACK
    c_timebox_border_free: graphics.Color = COLOR_BLACK

    c_separator: graphics.Color = COLOR_GREY_DARKEST


@dataclass
class Booking:
    courtname_truncate_to: int = 2

    c_clock: graphics.Color = COLOR_WHITE
    f_clock: graphics.Font = FONT_XL_SDK  # FONT_CLOCK_DEFAULT # FONT_L

    c_timebox: graphics.Color = COLOR_GREY
    c_timebox_countdown: graphics.Color = COLOR_7C_GOLD
    c_free_to_book: graphics.Color = COLOR_7C_GREEN

    is_weather_displayed: bool = True

    one: OneCourt = OneCourt()
    many: MultipleCourts = MultipleCourts()


@dataclass
class ClubStyle:
    ci: ClubCI = ClubCI()
    booking: Booking = Booking()


# TABB Böblingen
COLOR_CI_TABB_1 = graphics.Color(int("0x29", 0), int("0x49", 0), int("0x75", 0))
COLOR_CI_TABB_2 = COLOR_GREY_DARK
style_TABB = ClubStyle(
    ci=ClubCI(
        c_bg_1=COLOR_CI_TABB_1,
        c_bg_2=COLOR_CI_TABB_2,
        logo=Logo(path="images/logos/TABB/tabb-logo-transparent-60x13-border-3.png"),
    ),
    booking=Booking(is_weather_displayed=True, courtname_truncate_to=3),
)

# SV1845 Esslingen
COLOR_CI_SV1845_1 = graphics.Color(
    int("0x29", 0), int("0x49", 0), int("0x75", 0)
)  # Blue
COLOR_CI_SV1845_2 = graphics.Color(
    int("0xC9", 0), int("0x42", 0), int("0x40", 0)
)  # Red
style_SV1845 = ClubStyle(
    ci=ClubCI(
        c_bg_1=COLOR_CI_SV1845_1,
        c_bg_2=COLOR_CI_SV1845_2,
        logo=Logo(
            path="images/logos/SV1845/sv1845_76x64_eBusy_demo_logo.png",
            round_corners=True,
        ),
    ),
    booking=Booking(is_weather_displayed=False),
)

# Matchcenter Filderstadt
COLOR_CI_Matchcenter_1 = COLOR_GREY_DARKEST  # Black
COLOR_CI_Matchcenter_2 = graphics.Color(
    int("0xE5", 0), int("0x00", 0), int("0x7D", 0)
)  # Magenta
style_MatchCenter = ClubStyle(
    ci=ClubCI(
        c_bg_1=COLOR_CI_Matchcenter_1,
        c_bg_2=COLOR_CI_Matchcenter_2,
        logo=Logo(
            path="images/logos/MatchCenter Filderstadt/logo-matchcenter_58x39.png"
        ),
    ),
    booking=Booking(
        is_weather_displayed=False, one=OneCourt(is_court_name_on_top=False)
    ),
)

# SevenCourts
COLOR_CI_SevenCourts_1 = COLOR_7C_DARK_BLUE
COLOR_CI_SevenCourts_2 = COLOR_7C_DARK_GREEN
style_SevenCourts = ClubStyle(
    ci=ClubCI(
        c_bg_1=COLOR_CI_SevenCourts_1,
        c_bg_2=COLOR_CI_SevenCourts_2,
        logo=Logo(path="images/logos/SevenCourts/sevencourts_58x6.png"),
    ),
    booking=Booking(
        is_weather_displayed=True, one=OneCourt(is_court_name_on_top=False)
    ),
)


# B-W Vaihingen-Rohr, Stuttgart
COLOR_BW_VAIHINGEN_ROHR_BLUE = graphics.Color(0x09, 0x65, 0xA6)  # #0965A6
