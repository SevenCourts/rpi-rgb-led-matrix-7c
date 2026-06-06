"""M1 Layout — values extracted verbatim from the original M1 view modules.

This is a faithful extraction; any deviation here changes M1 visual output.
"""

from sevencourts.rgbmatrix import (
    COLOR_7C_BLUE,
    COLOR_7C_DARK_GREEN,
    COLOR_7C_DARK_GREY,
    COLOR_BLACK,
    COLOR_CLOCK_DEFAULT,
    COLOR_DEEP_ORANGE,
    COLOR_GOLD,
    COLOR_GREY,
    COLOR_WHITE,
    COLOR_YELLOW,
    FONT_L,
    FONT_L_7SEGMENT,
    FONT_L_SPLEEN,
    FONT_M,
    FONT_S,
    FONT_S_SPLEEN,
    FONT_XL,
    FONT_XL_7SEGMENT,
    FONT_XL_SDK,
    FONT_XL_SPLEEN,
    FONT_XS_SPLEEN,
    FONT_XXL_7SEGMENT,
    FONT_XXL_SPLEEN,
)

from sevencourts.m1.dimens import FONT_CLOCK_DEFAULT, H_PANEL, W_LOGO_WITH_CLOCK, W_PANEL
from sevencourts.m1.layouts.types import (
    ClockLayout,
    ImageLayout,
    Layout,
    MessageLayout,
    ScoreboardLayout,
    SignageLayout,
)


SCOREBOARD = ScoreboardLayout(
    color_score_set=COLOR_WHITE,
    color_score_set_won=COLOR_WHITE,
    color_score_set_lost=COLOR_GREY,
    color_score_game=COLOR_WHITE,
    color_score_service=COLOR_YELLOW,
    color_team_name=COLOR_WHITE,
    color_score_background=COLOR_BLACK,
    font_score=FONT_XL_SDK,
    font_score_set=FONT_XL_SDK,
    font_name_candidates=[FONT_L, FONT_M, FONT_S],
    upper_case_names=True,
    margin_names_scoreboard=3,
    x_min_scoreboard=W_PANEL // 2,
    w_score_set=20,
    x_score_game=163,
    x_score_service=155,
    # Cup matches L1/XL1 sizing (was scale=1). 2× cup is 18×20; centred in
    # the 32-px team half ((32 - 20) // 2 = 6).
    winner_scale=2,
    winner_y_t1=6,
    winner_y_t2=38,
)


CLOCK = ClockLayout(
    font_clock_s_1=FONT_L_7SEGMENT,
    font_clock_m_1=FONT_XL_7SEGMENT,
    font_clock_l_1=FONT_XXL_7SEGMENT,
    font_clock_s_2=FONT_L_SPLEEN,
    font_clock_m_2=FONT_XL_SPLEEN,
    font_clock_l_2=FONT_XXL_SPLEEN,
)


IMAGE = ImageLayout()


MESSAGE = MessageLayout(
    color_message=COLOR_7C_BLUE,
    font_candidates=[FONT_L, FONT_M, FONT_S],
    # Legacy M1 clock placement (matches `view_clock.draw_clock(cnv, t, None)`).
    clock_x=W_LOGO_WITH_CLOCK,
    clock_y=H_PANEL - 2,
    clock_font=FONT_CLOCK_DEFAULT,
    clock_color=COLOR_CLOCK_DEFAULT,
    clock_right_aligned=False,
    clock_divider_y=None,
    color_clock_divider=COLOR_BLACK,
)


SIGNAGE = SignageLayout(
    font_court_name=FONT_XS_SPLEEN,
    font_team_name=FONT_XS_SPLEEN,
    font_score=FONT_S_SPLEEN,
    color_score=COLOR_WHITE,
    color_score_won=COLOR_WHITE,
    color_score_lost=COLOR_GREY,
    color_match_bg=COLOR_BLACK,
    color_court_name=COLOR_DEEP_ORANGE,
    color_court_name_bg=COLOR_7C_DARK_GREY,
    color_team_name=COLOR_GREY,
    color_setscore_completed_won_bg=COLOR_7C_DARK_GREEN,
    color_srv=COLOR_YELLOW,
    color_gamescore=COLOR_WHITE,
    color_match_status=COLOR_GOLD,
    max_length_name_singles=14,
    max_length_name_doubles=3,
)


LAYOUT = Layout(
    scoreboard=SCOREBOARD,
    clock=CLOCK,
    image=IMAGE,
    message=MESSAGE,
    signage=SIGNAGE,
)
