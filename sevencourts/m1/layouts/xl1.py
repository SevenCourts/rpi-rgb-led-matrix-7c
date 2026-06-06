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
    COLOR_DEEP_ORANGE,
    COLOR_GOLD,
    COLOR_GREY,
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
    # Service indicator sized 11 px (see service_ball_size below). Right edge
    # at 280 leaves a 1-px gap before the game column (x=282). Left side has
    # 5 px to the last visible set-3 ink (~x=264), avoiding any overlap.
    x_score_service=270,
    # Center single-char game scores ("A") horizontally inside the 2-char slot.
    # Half-advance (17 / 2 ≈ 9) shifts a 1-char glyph to the slot center.
    dx_score_game_single_digit=9,
    # 11-px ball (≈1.5× the M1/L1 default 7) — bigger feels right next to the
    # FONT_L_7SEGMENT score; positioning logic centres it on the score-digit mid.
    service_ball_size=11,
    # Doubles spacing: 3 px between p1/p2 within a team, 7 px between teams.
    doubles_gap_within_team=3,
    doubles_gap_between_teams=7,
    # Cup: 9×10 source resized proportionally to 23×25 (5 px shorter than
    # the natural 3× → 27×30, but aspect-preserved). 25 = FONT_L_7SEGMENT
    # glyph height; cup top y=11 matches the score-glyph top
    # (baseline 36 − 25 = 11), so cup and score align at their top edges.
    winner_scale=3,
    winner_target_w=23,
    winner_target_h=25,
    winner_y_t1=11,
    winner_y_t2=59,
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
# full white so it reads clearly alongside the message text.
MESSAGE = MessageLayout(
    color_message=COLOR_7C_BLUE,
    font_candidates=[FONT_XXL_SPLEEN, FONT_XL, FONT_L_SPLEEN, FONT_M_SPLEEN, FONT_S_SPLEEN],
    clock_x=None,  # unused when right-aligned
    clock_y=95,
    clock_font=FONT_L_7SEGMENT,
    clock_color=COLOR_WHITE,
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
    # Match font_team_name (was FONT_M_SPLEEN; the heavier 8×16 glyphs read as
    # bold next to the 6×12 names AND eat enough width to clip the 5th doubles
    # name character).
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
    max_length_name_singles=12,
    max_length_name_doubles=7,
    # Flush-left so the flag (and doubles name block) starts at the same x
    # as the blue court-name header background. Right padding kept at 3 so
    # the score column doesn't kiss the cell edge.
    cell_padding_left=0,
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
