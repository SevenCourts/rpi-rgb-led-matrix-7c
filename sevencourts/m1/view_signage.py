# Horizontal signage for arbitrary tournament (e.g. ITF, etc.)
# Displays up to 4 matches / courts simultaneously

from typing import List

from PIL import Image

import sevencourts.images as imgs
from sevencourts.m1.dimens import *
from sevencourts.m1.layouts import current_layout
from sevencourts.rgbmatrix import *

VOID_TEAM = {"name": None, "country": None}

W_MATCH = W_PANEL // 2
H_MATCH = H_PANEL // 2


def draw(canvas, signage_info):
    layout = current_layout().signage
    geom = _Geometry(layout)

    fill_rect(canvas, 0, 0, W_PANEL, H_PANEL, layout.color_match_bg)

    for court_pos, court in enumerate(signage_info.get("courts", [])):
        court_name = court.get("name", "Court " + str(court_pos + 1))
        team1 = court.get("team1")
        team2 = court.get("team2")
        score_sets = court.get("score-sets")
        score_game = court.get("score-game")
        is_serving_t1 = court.get("is-serving-t1")
        match_status = court.get("match-status")

        _display_match(
            canvas,
            court_pos,
            court_name,
            team1,
            team2,
            score_sets,
            score_game,
            is_serving_t1,
            match_status,
            layout,
            geom,
        )


class _Geometry:
    """Derived font metrics; computed once per draw to avoid repeated dict lookups."""

    def __init__(self, layout):
        self.h_font_court_name = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(layout.font_court_name)
        self.h_font_team_name = max(
            Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(layout.font_team_name),
            Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(layout.font_score),
        )


def _match_coordinates(court_pos: int):
    x = 0 if (court_pos % 2) == 0 else W_MATCH
    y = 0 if (court_pos < 2) else H_MATCH
    return [x, y]


def _draw_flag(canvas, x, y, flag_code=None, small=False):
    image = imgs.load_flag_image(flag_code)
    if small:
        image.thumbnail((W_FLAG_SMALL, H_FLAG_SMALL), Image.LANCZOS)
    canvas.SetImage(image, x, y)


def _display_team_player(
    canvas, x0, y0, player_index, name, flag_code, layout, geom
):
    font = layout.font_team_name

    # relevant only for doubles, otherwise 0
    x_shift = player_index * (
        W_FLAG_SMALL
        + 1
        + width_in_pixels(font, " " * layout.max_length_name_doubles)
    )

    x_content = x0 + layout.cell_padding_left
    x_flag = x_content + x_shift
    y_flag = y0
    _draw_flag(canvas, x_flag, y_flag, flag_code, True)

    y_name = y0 + Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(font)
    x_name = x_content + x_shift + W_FLAG_SMALL + 1
    draw_text(canvas, x_name, y_name, name, font, layout.color_team_name)


def _display_team_score(
    canvas, x0, y0, score_sets_with_color, score_game, is_serving, layout, geom
):
    font = layout.font_score
    h_font_team_name = geom.h_font_team_name
    y = y0 + Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(font)

    # RTL
    # 1. game score
    w_score_game = width_in_pixels(font, score_game)
    w_score_game_max = width_in_pixels(font, "Ad")
    x_score_game = x0 + W_MATCH - layout.cell_padding_right - (w_score_game_max + w_score_game) // 2

    # this is an indirect indication of whether match is started or not
    # TODO make it more explicit (needs server changes)
    is_some_score_present = (
        score_sets_with_color is not None and len(score_sets_with_color) > 0
    )

    if is_some_score_present:
        fill_rect(
            canvas,
            x0 + W_MATCH - layout.cell_padding_right - w_score_game_max,
            y,
            w_score_game_max - 1,
            -h_font_team_name,
            layout.color_match_bg,
        )
        fill_rect(
            canvas,
            x0 + W_MATCH - layout.cell_padding_right - w_score_game_max,
            y + 1,
            w_score_game_max,
            1,
            layout.color_match_bg,
        )

        draw_text(canvas, x_score_game, y, score_game, font, layout.color_gamescore)

        # 2. service indicator
        b = rgb_list(layout.color_match_bg)
        o = rgb_list(layout.color_srv)
        service_indicator = [[b, o, o, b], [o, o, o, o], [o, o, o, o], [b, o, o, b]]
        w_indicator = len(service_indicator[0])
        x_indicator = x0 + W_MATCH - layout.cell_padding_right - w_score_game_max - w_indicator - 1
        y_indicator = y0 + 2

        fill_rect(
            canvas,
            x_indicator,
            y + 1,
            w_indicator + 1,
            -h_font_team_name - 1,
            layout.color_match_bg,
        )

        if is_serving:
            draw_matrix(canvas, service_indicator, x_indicator, y_indicator)

        # sets scores
        x_score_set = x_indicator + 1
        for ss in score_sets_with_color[::-1]:
            score_set, color = ss
            # FIXME bug when match is completed
            # TODO no background if the set is lost
            c = layout.color_match_bg
            score = str(score_set)
            w_score = width_in_pixels(font, score)
            # FIXME potential ui bug when score is more than 2 digits
            x_score_set -= w_score + 2

            fill_rect(
                canvas,
                x_score_set - 1,
                y + 1,
                w_score + 2,
                -h_font_team_name - 1,
                layout.color_match_bg,
            )
            fill_rect(
                canvas,
                x_score_set + w_score,
                y,
                1,
                -h_font_team_name,
                layout.color_match_bg,
            )
            fill_rect(canvas, x_score_set - 1, y, w_score + 1, -h_font_team_name, c)

            draw_text(canvas, x_score_set, y, score, font, color)

    return h_font_team_name + 3


def _display_team(
    canvas, x0, y_team, team, score_sets, is_serving, score_game, layout, geom
):
    if team is None:
        return 0

    is_doubles = team.get("p2") is not None

    if team["p1"]["name"] is not None:
        p1_name = team["p1"]["name"]
        p1_flag = team["p1"]["flag"]

        if is_doubles:
            p1_name = p1_name[: layout.max_length_name_doubles].upper()
            _display_team_player(canvas, x0, y_team, 0, p1_name, p1_flag, layout, geom)

            p2_name = team["p2"]["name"]
            p2_flag = team["p2"]["flag"]
            p2_name = p2_name[: layout.max_length_name_doubles].upper()
            _display_team_player(canvas, x0, y_team, 1, p2_name, p2_flag, layout, geom)
        else:
            p1_name = p1_name[: layout.max_length_name_singles]
            _display_team_player(canvas, x0, y_team, 0, p1_name, p1_flag, layout, geom)
        return _display_team_score(
            canvas, x0, y_team, score_sets, score_game, is_serving, layout, geom
        )
    else:
        return 0


def _display_court_name(canvas, x, y, court_name, match_status, layout, geom):
    font = layout.font_court_name
    w_bg = W_MATCH - 1
    h_bg = geom.h_font_court_name + 2
    fill_rect(canvas, x, y, w_bg, h_bg, layout.color_court_name_bg)

    x_court_name = x + 1 + layout.cell_padding_left
    y_court_name = y + geom.h_font_court_name + 1
    draw_text(canvas, x_court_name, y_court_name, court_name, font, layout.color_court_name)

    if match_status is not None:
        x_time = x + W_MATCH - layout.cell_padding_right - width_in_pixels(font, match_status) - 1
        y_time = y_court_name
        draw_text(canvas, x_time, y_time, match_status, font, layout.color_match_status)

    return h_bg


def _display_match(
    canvas,
    court_pos,
    court_name,
    team1,
    team2,
    score_sets,
    score_game,
    is_serving_t1,
    match_status,
    layout,
    geom,
):
    x0, y0 = _match_coordinates(court_pos)

    fill_rect(canvas, x0, y0, W_MATCH, H_MATCH, layout.color_match_bg)

    # 1. Court name
    y_shift = _display_court_name(canvas, x0, y0, court_name, match_status, layout, geom)

    # 2. Teams
    score_sets_t1: List = []
    score_sets_t2: List = []
    for ss in score_sets or []:
        # TODO handle match finished state
        colors = score_colors(ss[0], ss[1], True, layout)
        score_sets_t1.append((ss[0], colors[0]))
        score_sets_t2.append((ss[1], colors[1]))

    score_game_t1 = str(score_game[0]) if score_game else ""
    y_t1 = y0 + y_shift + layout.gap_title_to_team
    y_shift = _display_team(
        canvas, x0, y_t1, team1, score_sets_t1, is_serving_t1, score_game_t1, layout, geom
    )

    score_game_t2 = str(score_game[1]) if score_game else ""
    y_t2 = y_t1 + y_shift
    is_serving_t2 = None if is_serving_t1 is None else not is_serving_t1
    _display_team(
        canvas, x0, y_t2, team2, score_sets_t2, is_serving_t2, score_game_t2, layout, geom
    )


def _color(t1, t2, layout):
    if t1 == t2:
        return layout.color_score
    elif t1 > t2:
        return layout.color_score_won
    else:
        return layout.color_score_lost


def score_colors(t1, t2, finished, layout):
    if finished and t1 and t2:
        return [_color(t1, t2, layout), _color(t2, t1, layout)]
    return [layout.color_score, layout.color_score]
