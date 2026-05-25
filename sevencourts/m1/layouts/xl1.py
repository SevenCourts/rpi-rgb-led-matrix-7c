"""XL1 Layout — values for the 320×96 panel.

Authoritative source: `spec/xl1-layouts/decisions.md`. The mockup-renderer in
`spec/xl1-layouts/mockups/render.py` documents the exact pixel geometry the
firmware reproduces here.
"""

from sevencourts.rgbmatrix import (
    COLOR_7C_BLUE,
    COLOR_7C_DARK_GREEN,
    COLOR_7C_DARK_GREY,
    COLOR_BLACK,
    COLOR_GOLD,
    COLOR_GREY,
    COLOR_GREY_DARK,
    COLOR_WHITE,
    COLOR_YELLOW,
    FONT_L_7SEGMENT,
    FONT_L_SPLEEN,
    FONT_M_SPLEEN,
    FONT_S_SPLEEN,
    FONT_XL,
    FONT_XL_7SEGMENT,
    FONT_XXL_7SEGMENT,
    FONT_XXL_SPLEEN,  # used by MessageLayout
)
import sevencourts.club_styles as club_styles

from sevencourts.m1.layouts.types import (
    ClockLayout,
    ImageLayout,
    Layout,
    MessageLayout,
    ScoreboardLayout,
    SignageLayout,
)


# --- Scoreboard ---------------------------------------------------------------
# Score zone is content-sized starting at x=170 (decisions.md):
#   set columns x=170..235 (3 × 22px) | service indicator centered at x≈245
#   | game score in FONT_XL_7SEGMENT right-aligned at x=316.
# `x_score_service` value 242 places the 7px service ball centered at x≈245
# (242 + 3 = 245), matching mockup `scoreboard_native.png`.
SCOREBOARD = ScoreboardLayout(
    color_score_set=COLOR_WHITE,
    color_score_set_won=COLOR_WHITE,
    color_score_set_lost=COLOR_GREY,
    color_score_game=COLOR_WHITE,
    color_score_service=COLOR_YELLOW,
    color_team_name=COLOR_WHITE,
    color_score_background=COLOR_BLACK,
    # Game score: FONT_L_7SEGMENT (25-px glyph, 17-px advance). Preserves the
    # 7-segment scoreboard aesthetic; smaller than the earlier 40-/44-px
    # variants per bench feedback. 7-seg BDFs ship digits only, so "Ad" is
    # encoded as "A" in fixtures/data.
    font_score=FONT_L_7SEGMENT,
    # Set digits: FONT_L_7SEGMENT (same family as font_score for visual
    # consistency — both set and game scores share the 7-segment look).
    # Hex letters (A, b, C, d, E, F) were added to the BDF via
    # `tools/add_7segment_letters.py` so values like "Ad" render correctly.
    font_score_set=FONT_L_7SEGMENT,
    font_name_candidates=[FONT_XL, FONT_L_SPLEEN, FONT_M_SPLEEN, FONT_S_SPLEEN],
    upper_case_names=True,
    margin_names_scoreboard=3,
    # Score zone packed close to the game-score column. Set3-column ink ends
    # at x=263 leaving a 9-px gap (~half a FONT_L_7SEGMENT advance) before the
    # service ball at x=273. Name zone is the rest (x=0..203).
    x_min_scoreboard=204,
    w_score_set=22,
    # Game score right-aligned: 2 × 17-px advance = 34 px → starts at x=282.
    x_score_game=282,
    # Service indicator nestled between set3 column (ends ~x=269) and game
    # column (starts at x=282); ball is 7 px wide so 273..279 leaves a 2-px gap.
    x_score_service=273,
    # Center single-char game scores ("A") horizontally inside the 2-char slot.
    # Half-advance (17 / 2 ≈ 9) shifts a 1-char glyph to the slot center.
    dx_score_game_single_digit=9,
    # Doubles spacing: 2 px between p1/p2 within a team, 10 px between teams.
    doubles_gap_within_team=2,
    doubles_gap_between_teams=10,
    # 2× cup matrix (9×10 → 18×20 px), vertically centered in each team half
    # ((48 - 20) // 2 = 14 from team top).
    winner_scale=2,
    winner_y_t1=14,
    winner_y_t2=62,  # 48 (team-2 top) + 14
)


# --- Clock --------------------------------------------------------------------
# On XL1 the 96px panel fits FONT_XXL_7SEGMENT (66px glyph) cleanly.
CLOCK = ClockLayout(
    font_clock_s_1=FONT_L_7SEGMENT,
    font_clock_m_1=FONT_XL_7SEGMENT,
    font_clock_l_1=FONT_XXL_7SEGMENT,
    font_clock_s_2=FONT_L_SPLEEN,
    font_clock_m_2=FONT_XL,  # spleen-16x32
    font_clock_l_2=FONT_XXL_SPLEEN,
)


# --- Image --------------------------------------------------------------------
IMAGE = ImageLayout()


# --- Message ------------------------------------------------------------------
# XL1 message view: right-aligned FONT_L_7SEGMENT clock at baseline y=95,
# color COLOR_GREY_DARK so it doesn't compete with the message text.
MESSAGE = MessageLayout(
    color_message=COLOR_7C_BLUE,
    font_candidates=[FONT_XXL_SPLEEN, FONT_XL, FONT_L_SPLEEN, FONT_M_SPLEEN, FONT_S_SPLEEN],
    clock_x=None,  # unused when right-aligned
    clock_y=95,
    clock_font=FONT_L_7SEGMENT,
    clock_color=COLOR_GREY_DARK,
    clock_right_aligned=True,
    clock_divider_y=None,
    color_clock_divider=COLOR_7C_DARK_GREY,
)


# --- Signage -----------------------------------------------------------------
# Cell size on XL1 is 160×48 (W_MATCH = W_PANEL//2, H_MATCH = H_PANEL//2).
# Fonts upgrade one notch vs M1: XS→S for names, S→M for game scores.
# `max_length_name_singles=12` (decisions.md): mockup geometry supports 12 at
# FONT_S_SPLEEN; 15 was aspirational and revisited on the bench.
SIGNAGE = SignageLayout(
    font_court_name=FONT_S_SPLEEN,
    font_team_name=FONT_S_SPLEEN,
    font_score=FONT_M_SPLEEN,
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
    max_length_name_singles=12,
    max_length_name_doubles=5,
    cell_padding_left=3,
    cell_padding_right=3,
    gap_title_to_team=5,
)


LAYOUT = Layout(
    scoreboard=SCOREBOARD,
    clock=CLOCK,
    image=IMAGE,
    message=MESSAGE,
    signage=SIGNAGE,
)
