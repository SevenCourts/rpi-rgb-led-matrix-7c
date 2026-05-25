"""L1 Layout — values for the 192×96 panel.

L1 is M1's width with XL1's height. So horizontal coordinates mostly mirror
M1 (score-zone budget is unchanged), while vertical fields take advantage of
the taller canvas: bigger cup, more doubles breathing room, FONT_XL message
option, etc. Flags share XL1's 27×18 size.
"""

from sevencourts.rgbmatrix import (
    COLOR_7C_BLUE,
    COLOR_7C_DARK_GREEN,
    COLOR_BLACK,
    COLOR_CLOCK_DEFAULT,
    COLOR_GOLD,
    COLOR_GREY,
    COLOR_WHITE,
    COLOR_YELLOW,
    FONT_L,
    FONT_L_7SEGMENT,
    FONT_L_SPLEEN,
    FONT_M,
    FONT_M_SPLEEN,
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
import sevencourts.club_styles as club_styles

from sevencourts.m1.dimens import FONT_CLOCK_DEFAULT, H_PANEL, W_LOGO_WITH_CLOCK, W_PANEL
from sevencourts.m1.layouts.types import (
    ClockLayout,
    ImageLayout,
    Layout,
    MessageLayout,
    ScoreboardLayout,
    SignageLayout,
)


# --- Scoreboard ---------------------------------------------------------------
# Width matches M1, so x-coordinates are M1's values verbatim. The 27×18 flag
# (from dimens.py) eats 9 more px on the left than M1's 18×12 — the name-font
# cascade in pick_font_that_fits handles longer names by falling back to FONT_M/S.
SCOREBOARD = ScoreboardLayout(
    color_score_set=COLOR_WHITE,
    color_score_set_won=COLOR_WHITE,
    color_score_set_lost=COLOR_GREY,
    color_score_game=COLOR_WHITE,
    color_score_service=COLOR_YELLOW,
    color_team_name=COLOR_WHITE,
    color_score_background=COLOR_BLACK,
    # M1 fonts: width is unchanged from M1, so XL1's bigger 7-segment fonts
    # crowd the score zone. Bench feedback prefers M1 sizing.
    font_score=FONT_XL_SDK,
    font_score_set=FONT_XL_SDK,
    font_name_candidates=[FONT_L, FONT_M, FONT_S],
    upper_case_names=True,
    margin_names_scoreboard=3,
    # Horizontal layout identical to M1 (width unchanged).
    x_min_scoreboard=W_PANEL // 2,
    w_score_set=20,
    x_score_game=163,
    x_score_service=155,
    # L1-specific vertical spacing: leverages H_PANEL=96 (vs M1's 64).
    doubles_gap_within_team=2,
    doubles_gap_between_teams=10,
    # 2× cup, vertically centered in the 48-px team half.
    winner_scale=2,
    winner_y_t1=14,
    winner_y_t2=62,
)


# --- Clock --------------------------------------------------------------------
# Same horizontal budget as M1, so font choices match. L1's extra vertical
# height makes the large 7-segment / Spleen variants fit cleanly.
CLOCK = ClockLayout(
    font_clock_s_1=FONT_L_7SEGMENT,
    font_clock_m_1=FONT_XL_7SEGMENT,
    font_clock_l_1=FONT_XXL_7SEGMENT,
    font_clock_s_2=FONT_L_SPLEEN,
    font_clock_m_2=FONT_XL_SPLEEN,
    font_clock_l_2=FONT_XXL_SPLEEN,
)


# --- Image --------------------------------------------------------------------
IMAGE = ImageLayout()


# --- Message ------------------------------------------------------------------
# FONT_XL added as first candidate so short single-line messages get the
# 20-px glyph treatment when they fit (L1's 76-px message zone has room).
MESSAGE = MessageLayout(
    color_message=COLOR_7C_BLUE,
    font_candidates=[FONT_XL, FONT_L, FONT_M, FONT_S],
    # Legacy M1 clock placement preserved (width unchanged).
    clock_x=W_LOGO_WITH_CLOCK,
    clock_y=H_PANEL - 2,
    clock_font=FONT_CLOCK_DEFAULT,
    clock_color=COLOR_CLOCK_DEFAULT,
    clock_right_aligned=False,
    clock_divider_y=None,
    color_clock_divider=COLOR_BLACK,
)


# --- Signage -----------------------------------------------------------------
# Cells are 96×48 — same width as M1, taller by 16 px. Fonts stay M1-sized
# because the width budget hasn't grown; doubles names get more vertical
# room and can extend from 3 → 5 characters.
SIGNAGE = SignageLayout(
    # M1 fonts — narrower cells need tighter glyphs.
    font_court_name=FONT_XS_SPLEEN,
    font_team_name=FONT_XS_SPLEEN,
    font_score=FONT_S_SPLEEN,
    color_score=COLOR_WHITE,
    color_score_won=COLOR_WHITE,
    color_score_lost=COLOR_GREY,
    color_match_bg=COLOR_BLACK,
    color_court_name=COLOR_GREY,
    color_court_name_bg=club_styles.COLOR_BW_VAIHINGEN_ROHR_BLUE,
    color_team_name=COLOR_GREY,
    color_setscore_completed_won_bg=COLOR_7C_DARK_GREEN,
    color_srv=COLOR_GREY,
    color_gamescore=COLOR_WHITE,
    color_match_status=COLOR_GOLD,
    max_length_name_singles=14,
    # Doubles benefit from L1's extra vertical room (48-px cells vs M1's 32).
    max_length_name_doubles=5,
    cell_padding_left=0,
    cell_padding_right=0,
    # Slightly more breathing room than M1's default (2) — L1 has the vertical budget.
    gap_title_to_team=4,
)


LAYOUT = Layout(
    scoreboard=SCOREBOARD,
    clock=CLOCK,
    image=IMAGE,
    message=MESSAGE,
    signage=SIGNAGE,
)
