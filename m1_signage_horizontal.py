# Horizontal signage for arbitrary tournament (e.g. ITF, etc.)
# Displays up to 4 matches / courts simultaneously

from sevencourts import *
from m1_signage import *

from typing import List

FONT_SIGNAGE_COURT_NAME = FONT_XS_SPLEEN # 5x8
FONT_SIGNAGE_TEAM_NAME = FONT_S_SPLEEN # 6x12
FONT_SIGNAGE_SCORE = FONT_S_SPLEEN # 6x12

h_font_court_name = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_SIGNAGE_COURT_NAME)
h_font_team_name = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_SIGNAGE_TEAM_NAME)


COLOR_SIGNAGE_COURT_NAME = COLOR_GREY
COLOR_SIGNAGE_COURT_NAME_BG = COLOR_BW_VAIHINGEN_ROHR_BLUE
COLOR_SIGNAGE_TEAM_NAME = COLOR_WHITE
COLOR_SIGNAGE_SCORE = COLOR_WHITE

VOID_TEAM = ["", None]

MAX_LENGTH_NAME_SINGLES = 14
MAX_LENGTH_NAME_DOUBLES = 3

W_MATCH = int(W_PANEL / 2)
H_MATCH = int(H_PANEL / 2)

def _match_coordinates (court_pos: int):
    x = 0 if (court_pos % 2) == 0 else W_MATCH
    y = 0 if (court_pos < 2) else H_MATCH
    return [x, y]

def _display_player(canvas, x0: int, y0: int, player_index: int, name :str, flag_code :str):
    font = FONT_SIGNAGE_TEAM_NAME
    
    # relevant only for doubles, otherwise 0
    x_shift = player_index * (W_FLAG_SMALL + 1 + width_in_pixels(font, " " * MAX_LENGTH_NAME_DOUBLES))
    
    x_flag = x0 + x_shift
    y_flag = y0 + 1
    draw_flag(canvas, x_flag, y_flag, flag_code, True)

    y_name = y0 + Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(font)
    x_name = x0 + x_shift + W_FLAG_SMALL + 1
    draw_text(canvas, x_name, y_name, name, font, COLOR_SIGNAGE_TEAM_NAME)

def _display_team_score(canvas, x0: int, y0: int, score_sets: List[int], score_game: str, is_serving: bool):
    font = FONT_SIGNAGE_SCORE
    x_shift = (W_FLAG_SMALL + 1 + width_in_pixels(FONT_SIGNAGE_TEAM_NAME, " " * MAX_LENGTH_NAME_SINGLES))
    y = y0 + Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(font)

    # sets scores
    x = x0 + x_shift
    for score_set in score_sets:
        score = str(score_set)
        draw_text(canvas, x, y, score, font, COLOR_SIGNAGE_SCORE)
        x += width_in_pixels(font, score) + 1
    
    # service indicator
    b = (0, 0, 0)
    w = (255, 255, 0)
    service_indicator = [
        [b, w, w, b],
        [w, w, w, w],
        [w, w, w, w],
        [b, w, w, b]]        
    if is_serving:
        y_indicator = y0 + 2
        draw_matrix(canvas, service_indicator, x, y_indicator)
    x += len(service_indicator[0]) + 1

    # game score
    draw_text(canvas, x, y, score_game, font, COLOR_SIGNAGE_SCORE)

    return h_font_team_name + 3

def _display_team(canvas, x0: int, y_team: int, team, score_sets, is_serving: bool, score_game: str):

    is_doubles = (team is not None and len(team) == 2)

    # TODO check idiomatic way to handle this
    if team is not None:
        p1_name, p1_flag = team[0]        
        p2_name, p2_flag = team[1] if is_doubles else VOID_TEAM
    else:
        p1_name, p1_flag = p2_name, p2_flag = VOID_TEAM        

    if (is_doubles):
        # P1
        p1_name = p1_name[:MAX_LENGTH_NAME_DOUBLES].upper()
        _display_player(canvas, x0, y_team, 0, p1_name, p1_flag)
        # P2
        p2_name = p2_name[:MAX_LENGTH_NAME_DOUBLES].upper()
        _display_player(canvas, x0, y_team, 1, p2_name, p2_flag)                

    else:
        p1_name = p1_name[:MAX_LENGTH_NAME_SINGLES]
        _display_player(canvas, x0, y_team, 0, p1_name, p1_flag)
    return _display_team_score(canvas, x0, y_team, score_sets, score_game, is_serving)

def _display_court_name(canvas, x: int , y: int, court_name: str, starting_time=None):
    font = FONT_SIGNAGE_COURT_NAME
    w_bg = W_MATCH - 1
    h_bg = h_font_court_name + 2
    fill_rect(canvas, x, y, w_bg, h_bg, COLOR_SIGNAGE_COURT_NAME_BG)
    
    x_court_name = x + 1
    y_court_name = y + h_font_court_name + 1
    draw_text(canvas, x_court_name, y_court_name, court_name, font, COLOR_SIGNAGE_COURT_NAME)

    if starting_time is not None:
        # Display starting time
        x_time = x + (W_MATCH - width_in_pixels(font, starting_time)) - 1
        y_time = y_court_name
        draw_text(canvas, x_time, y_time, starting_time, font, COLOR_SIGNAGE_COURT_NAME)

    return h_bg

def display_match(canvas, court_pos: int , court_name: str, 
                          team1: List[List[str]], team2: List[List[str]],
                          score_sets: List[int], score_game: List[str], is_serving_t1:bool, 
                          starting_time=None):
    x0, y0 = _match_coordinates(court_pos)

    # 1. Court name    
    x_court_name = x0
    y_court_name = y0
    y_shift = _display_court_name(canvas, x_court_name, y_court_name, court_name, starting_time)
    
    # 2. Team 1
    score_sets_t1 = [ss[0] for ss in score_sets] if score_sets else []
    score_game_t1 = str(score_game[0]) if score_game else ""
    y_t1 = y0 + y_shift + 1
    y_shift = _display_team(canvas, x0, y_t1, team1, score_sets_t1, is_serving_t1, score_game_t1)

    # 3. Team 2
    score_sets_t2 = [ss[1] for ss in score_sets] if score_sets else []
    score_game_t2 = str(score_game[1]) if score_game else ""
    y_t2 = y_t1 + y_shift
    is_serving_t2 = None if is_serving_t1 is None else not(is_serving_t1)
    _display_team(canvas, x0, y_t2, team2, score_sets_t2, is_serving_t2, score_game_t2)

def display_match_upcoming(canvas, court_pos: int , court_name: str, 
                           team1: List[List[str]], team2: List[List[str]],
                           starting_time: str):
    display_match(canvas, court_pos, court_name, team1, team2, None, None, None, starting_time)

    
