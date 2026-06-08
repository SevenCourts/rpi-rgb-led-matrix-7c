"""Per-view Layout dataclasses.

Each dataclass is the explicit contract between a view and the panel-type-specific
values it consumes (positions, fonts, colours, feature flags). Adding a field here
means a view started reading it; removing one means it stopped.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from sevencourts.rgbmatrix import graphics


@dataclass(frozen=True)
class ScoreboardLayout:
    color_score_set: graphics.Color
    color_score_set_won: graphics.Color
    color_score_set_lost: graphics.Color
    color_score_game: graphics.Color
    color_score_service: graphics.Color
    color_team_name: graphics.Color
    color_score_background: graphics.Color

    # Font for the game score column (large 7-segment digits).
    font_score: graphics.Font
    # Font for the set-score columns. M1 uses the same font as `font_score`; XL1
    # uses a smaller Spleen font so set digits don't compete with the game score.
    font_score_set: graphics.Font
    # `pick_font_that_fits` candidate list for player/team names.
    font_name_candidates: List[graphics.Font]

    upper_case_names: bool
    margin_names_scoreboard: int

    # Score-zone geometry: x positions for set columns, game score, service indicator.
    x_min_scoreboard: int
    w_score_set: int
    x_score_game: int
    x_score_service: int
    # x-shift applied to single-digit game scores so they right-align to the
    # same column edge as 2-digit values. One glyph advance in `font_score`.
    dx_score_game_single_digit: int = 8

    # Service indicator ball edge length (px). Must be odd and present in
    # view_scoreboard._BALL_PATTERNS (currently 7 or 11).
    service_ball_size: int = 7

    # Doubles name spacing (vertical px) — only used in doubles layout.
    doubles_gap_within_team: int = 1
    doubles_gap_between_teams: int = 4

    # Winner cup. `scale` magnifies the 9×10 cup matrix (each source pixel
    # becomes `scale`×`scale` panel pixels). `x` defaults to x_score_service
    # when -1. `y_t1` / `y_t2` are absolute cup top-edge coordinates;
    # `y_t2 = -1` means "y_t1 + H_PANEL // 2".
    # `target_h` / `target_w` override the natural `10 * scale` / `9 * scale`
    # dimensions — non-uniform values are realised by nearest-neighbour resize.
    winner_scale: int = 1
    winner_x: int = -1
    winner_y_t1: int = 12
    winner_y_t2: int = -1
    winner_target_w: int = -1
    winner_target_h: int = -1
    # Match-tie-break finishes also render the 2-digit deciding score in the
    # game-score column, so the normal cup would overlap it. When > 0, the cup
    # is shrunk to this height (width keeps the 9:10 aspect) and right-aligned
    # just left of `x_score_game` for tie-break results. -1 keeps the full cup.
    winner_mtb_h: int = -1
    # Horizontal nudge (px) for the shrunken MTB cup. The cup art carries a ~2px
    # transparent border, so right-aligning its box leaves a visible gap to the
    # score; a positive value shifts it right to close that gap per panel.
    winner_mtb_dx: int = 0


@dataclass(frozen=True)
class ClockLayout:
    # font-1 (default 7-segment family)
    font_clock_s_1: graphics.Font
    font_clock_m_1: graphics.Font
    font_clock_l_1: graphics.Font
    # font-2 (alternate Spleen family, selected via "font-2" key)
    font_clock_s_2: graphics.Font
    font_clock_m_2: graphics.Font
    font_clock_l_2: graphics.Font


@dataclass(frozen=True)
class ImageLayout:
    # Reserved: no panel-type-specific fields needed for M1.
    # `W_LOGO_WITH_CLOCK` and `H_PANEL` are read directly from dimens.
    pass


@dataclass(frozen=True)
class MessageLayout:
    color_message: graphics.Color
    # Optional override for `pick_font_that_fits`; None preserves the default M1 list.
    font_candidates: List[graphics.Font] = field(default_factory=list)

    # Clock placement inside the message view.
    # M1: clock_x = W_LOGO_WITH_CLOCK, clock_y = H_PANEL - 2,
    #     clock_font = FONT_CLOCK_DEFAULT, color = COLOR_CLOCK_DEFAULT (white),
    #     clock_right_aligned = False, clock_divider_y = None.
    # XL1: right-aligned 7-segment clock under a 1-px divider.
    clock_x: Optional[int] = None
    clock_y: Optional[int] = None
    clock_font: Optional[graphics.Font] = None
    clock_color: Optional[graphics.Color] = None
    clock_right_aligned: bool = False
    # Optional horizontal divider above the clock strip. None disables it.
    clock_divider_y: Optional[int] = None
    color_clock_divider: Optional[graphics.Color] = None


@dataclass(frozen=True)
class SignageLayout:
    font_court_name: graphics.Font
    font_team_name: graphics.Font
    font_score: graphics.Font

    color_score: graphics.Color
    color_score_won: graphics.Color
    color_score_lost: graphics.Color
    color_match_bg: graphics.Color
    color_court_name: graphics.Color
    color_court_name_bg: graphics.Color
    color_team_name: graphics.Color
    color_setscore_completed_won_bg: graphics.Color
    color_srv: graphics.Color
    color_gamescore: graphics.Color
    color_match_status: graphics.Color

    max_length_name_singles: int
    max_length_name_doubles: int

    # Per-cell padding inside the 2×2 grid. M1 had no padding (text was tight
    # against cell edges); XL1 has room to breathe.
    cell_padding_left: int = 0
    cell_padding_right: int = 0
    # Vertical gap between the court-name strip and the first team row.
    gap_title_to_team: int = 2


@dataclass(frozen=True)
class Layout:
    """Top-level Layout aggregating per-view layouts for the active panel type."""

    scoreboard: ScoreboardLayout
    clock: ClockLayout
    image: ImageLayout
    message: MessageLayout
    signage: SignageLayout
