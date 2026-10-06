from sevencourts.rgbmatrix import *
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Logo:
    path: str = None
    # Per-view emblems, for styles whose emblem is cut to the free area of one
    # view. Each falls back to `path` when unset.
    path_single: str = None
    path_multi: str = None
    round_corners: bool = False

    def single(self):
        return self.path_single or self.path

    def multi(self):
        return self.path_multi or self.path


@dataclass
class ClubCI:
    c_text: graphics.Color = COLOR_WHITE
    c_bg_1: graphics.Color = COLOR_7C_DARK_BLUE
    c_bg_2: graphics.Color = COLOR_7C_DARK_GREEN
    logo: Logo = field(default_factory=Logo)


@dataclass
class OneCourt:
    """
    Timebox is displayed on the left if True.
    Timebox is displayed above the clock if False.
    """

    is_court_name_on_top: bool = True
    """Otherwise the court name will be displayed on the left"""

    is_weather_in_header: bool = False
    """Temperature at the right end of the court-name header. Needs
    is_court_name_on_top and Booking.is_weather_displayed."""

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
    c_blocked: graphics.Color = COLOR_ORANGE

    is_weather_displayed: bool = True
    weather_city: str = "Stuttgart,DE"
    """OpenWeatherMap city the weather row is fetched for ("<name>,<country>")."""

    one: OneCourt = field(default_factory=OneCourt)
    many: MultipleCourts = field(default_factory=MultipleCourts)


@dataclass
class ClubStyle:
    ci: ClubCI = field(default_factory=ClubCI)
    booking: Booking = field(default_factory=Booking)


# TABB Böblingen
COLOR_CI_TABB_1 = graphics.Color(int("0x29", 0), int("0x49", 0), int("0x75", 0))
COLOR_CI_TABB_2 = COLOR_GREY_DARK
style_TABB = ClubStyle(
    ci=ClubCI(
        c_bg_1=COLOR_CI_TABB_1,
        c_bg_2=COLOR_CI_TABB_2,
        logo=Logo(path="images/logos/TABB/tabb-logo-transparent-60x13-border-3.png"),
    ),
    booking=Booking(
        is_weather_displayed=True,
        weather_city="Böblingen,DE",
        courtname_truncate_to=3,
    ),
)

# TC Heidelberg
COLOR_CI_TC_Heidelberg_1 = graphics.Color(
    int("0x3A", 0), int("0x43", 0), int("0x86", 0)
)
COLOR_CI_TC_Heidelberg_2 = COLOR_GREY_DARK
style_TC_Heidelberg = ClubStyle(
    ci=ClubCI(
        c_bg_1=COLOR_CI_TC_Heidelberg_1,
        c_bg_2=COLOR_CI_TC_Heidelberg_2,
        logo=Logo(path="images/logos/TC Heidelberg/HTC-Logo-78x64_black_bg.png"),
    ),
    booking=Booking(is_weather_displayed=False, courtname_truncate_to=3),
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

# Padel Club Esslingen (padelclubesslingen.de)
COLOR_CI_PadelClubEsslingen_GREEN = graphics.Color(0x29, 0x46, 0x3A)  # #29463A
COLOR_CI_PadelClubEsslingen_LIME = graphics.Color(0xD6, 0xDA, 0x63)  # #D6DA63
COLOR_CI_PadelClubEsslingen_CREAM = graphics.Color(0xF5, 0xF0, 0xE8)  # #F5F0E8
style_PadelClubEsslingen = ClubStyle(
    ci=ClubCI(
        c_text=COLOR_CI_PadelClubEsslingen_CREAM,
        c_bg_1=COLOR_CI_PadelClubEsslingen_GREEN,
        c_bg_2=COLOR_CI_PadelClubEsslingen_LIME,
        logo=Logo(
            # rendered by sevencourts.logoprep from padel-club-esslingen.recipe.json:
            # 64x30 fits the 66x32 free area of the single-court view, 64x25 the
            # multi-court view with the weather row; both are drawn unscaled
            path_single="images/logos/Padel Club Esslingen/m1/padel-club-esslingen_m1-booking-single_64x30.png",
            path_multi="images/logos/Padel Club Esslingen/m1/padel-club-esslingen_m1-booking-multi_64x25.png",
        ),
    ),
    booking=Booking(
        is_weather_displayed=True,
        weather_city="Esslingen am Neckar,DE",
        c_clock=COLOR_CI_PadelClubEsslingen_CREAM,
        c_timebox_countdown=COLOR_CI_PadelClubEsslingen_LIME,
        one=OneCourt(
            c_prompt=COLOR_CI_PadelClubEsslingen_LIME, is_weather_in_header=True
        ),
        many=MultipleCourts(c_weather=COLOR_CI_PadelClubEsslingen_CREAM),
    ),
)


STYLES: Dict[str, ClubStyle] = {
    "SevenCourts": style_SevenCourts,
    "SV1845": style_SV1845,
    "TABB": style_TABB,
    "MatchCenter": style_MatchCenter,
    "TC Heidelberg": style_TC_Heidelberg,
    "Padel Club Esslingen": style_PadelClubEsslingen,
}


def style_for(panel_info) -> ClubStyle:
    """The style the server selected in panel_info["booking"]["style"].

    Falls back to SevenCourts when there is no booking info or the name is
    unknown (e.g. a style newer than this firmware).
    """
    booking = (panel_info or {}).get("booking") or {}
    return STYLES.get(booking.get("style", "SevenCourts"), style_SevenCourts)


# B-W Vaihingen-Rohr, Stuttgart
COLOR_BW_VAIHINGEN_ROHR_BLUE = graphics.Color(0x09, 0x65, 0xA6)  # #0965A6
