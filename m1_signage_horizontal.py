# Horizontal signage for arbitrary tournament (e.g. ITF, etc.)
# Displays up to 4 matches / courts simultaneously

from sevencourts import *
from m1_signage import *

from typing import List

FONT_SIGNAGE_COURT_NAME = FONT_XS_SPLEEN # 5x8
FONT_SIGNAGE_TEAM_NAME = FONT_XS_SPLEEN # 5x8
FONT_SIGNAGE_SCORE = FONT_S_SPLEEN # 6x12

h_font_court_name = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_SIGNAGE_COURT_NAME)
h_font_team_name = max(
    Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_SIGNAGE_TEAM_NAME),
    Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_SIGNAGE_SCORE)    
)

COLOR_MATCH_BG = COLOR_BLACK
COLOR_COURT_NAME = COLOR_GREY
COLOR_COURT_NAME_BG = COLOR_BW_VAIHINGEN_ROHR_BLUE
COLOR_TEAM_NAME = COLOR_GREY
COLOR_SETSCORE_BG = COLOR_MATCH_BG
COLOR_SETSCORE_COMPLETED_WON_BG = COLOR_7C_GREEN_DARK
COLOR_SRV = COLOR_GREY
COLOR_SRV_BG = COLOR_MATCH_BG
COLOR_GAMESCORE = COLOR_WHITE
COLOR_GAMESCORE_BG = COLOR_MATCH_BG
COLOR_MATCH_STATUS = COLOR_7C_GOLD

VOID_TEAM = {"name": None, "country": None}


MAX_LENGTH_NAME_SINGLES = 14
MAX_LENGTH_NAME_DOUBLES = 3

W_MATCH = int(W_PANEL / 2)
H_MATCH = int(H_PANEL / 2)

def _match_coordinates (court_pos: int):
    x = 0 if (court_pos % 2) == 0 else W_MATCH
    y = 0 if (court_pos < 2) else H_MATCH
    return [x, y]

def _display_team_player(canvas, x0: int, y0: int, player_index: int, name :str, flag_code :str):
    font = FONT_SIGNAGE_TEAM_NAME
    
    # relevant only for doubles, otherwise 0
    x_shift = player_index * (W_FLAG_SMALL + 1 + width_in_pixels(font, " " * MAX_LENGTH_NAME_DOUBLES))
    
    x_flag = x0 + x_shift
    y_flag = y0
    draw_flag(canvas, x_flag, y_flag, flag_code, True)

    y_name = y0 + Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(font)
    x_name = x0 + x_shift + W_FLAG_SMALL + 1
    draw_text(canvas, x_name, y_name, name, font, COLOR_TEAM_NAME)

def _display_team_score(canvas, x0: int, y0: int, score_sets_with_color: List, score_game: str, is_serving: bool):
    font = FONT_SIGNAGE_SCORE
    y = y0 + Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(font)

    # RTL
    # 1. game score
    w_score_game = width_in_pixels(font, score_game)
    w_score_game_max = width_in_pixels(font, "Ad")
    x_score_game = x0 + W_MATCH - int((w_score_game_max + w_score_game) / 2)

    is_some_score_present = (score_game is not None and len(score_game) > 0) or (score_sets_with_color is not None and len(score_sets_with_color) > 0) or (is_serving is not None)
    if is_some_score_present: 
        fill_rect(canvas, x0 + W_MATCH - w_score_game_max, y,
                  w_score_game_max - 1, -h_font_team_name, COLOR_MATCH_BG)
        fill_rect(canvas, x0 + W_MATCH - w_score_game_max, y + 1,
                  w_score_game_max, 1, COLOR_MATCH_BG)

    draw_text(canvas, x_score_game, y, score_game, font, COLOR_GAMESCORE)

    # 2. service indicator
    b = rgb_list(COLOR_SRV_BG)
    o = rgb_list(COLOR_SRV)
    service_indicator = [
        [b, o, o, b],
        [o, o, o, o],
        [o, o, o, o],
        [b, o, o, b]]        
    w_indicator = len(service_indicator[0])
    x_indicator = x0 + W_MATCH - w_score_game_max - w_indicator - 1
    y_indicator = y0 + 2
    
    if is_some_score_present: 
        fill_rect(canvas, x_indicator, y + 1, w_indicator + 1, -h_font_team_name-1, COLOR_MATCH_BG)

    if is_serving:
        draw_matrix(canvas, service_indicator, x_indicator, y_indicator)
    
    # sets scores
    x_score_set = x_indicator + 1 # initial x position
    is_last_set = True
    for ss in score_sets_with_color[::-1]:
        score_set, color = ss
        # FIXME bug when match is completed
        # TODO no background if the set is lost
        c = COLOR_SETSCORE_BG # if is_last_set else COLOR_SETSCORE_COMPLETED_BG
        score = str(score_set)
        w_score = width_in_pixels(font, score)
        # FIXME potential ui bug when score is more than 2 digits
        x_score_set -= w_score + 2
        
        fill_rect(canvas, x_score_set - 1, y + 1, w_score + 2, -h_font_team_name-1, COLOR_MATCH_BG)
        fill_rect(canvas, x_score_set + w_score, y, 1, -h_font_team_name, COLOR_MATCH_BG)
        fill_rect(canvas, x_score_set - 1, y, w_score + 1, -h_font_team_name, c)
        
        # draw the score
        
        draw_text(canvas, x_score_set, y, score, font, color)
        is_last_set = False
    
    return h_font_team_name + 3

def _display_team(canvas, x0: int, y_team: int, team, score_sets, is_serving: bool, score_game: str):

    if (team is None):
        return 0

    is_doubles = (team.get('p2') is not None)

    if team['p1']['name'] is not None:
        p1_name = team['p1']['name']
        p1_flag = team['p1']['flag']

        if (is_doubles):
            # P1
            p1_name = p1_name[:MAX_LENGTH_NAME_DOUBLES].upper()
            _display_team_player(canvas, x0, y_team, 0, p1_name, p1_flag)

            # P2
            p2_name = team['p2']['name']
            p2_flag = team['p2']['flag']    
            p2_name = p2_name[:MAX_LENGTH_NAME_DOUBLES].upper()
            _display_team_player(canvas, x0, y_team, 1, p2_name, p2_flag)                

        else:
            p1_name = p1_name[:MAX_LENGTH_NAME_SINGLES]
            _display_team_player(canvas, x0, y_team, 0, p1_name, p1_flag)
        return _display_team_score(canvas, x0, y_team, score_sets, score_game, is_serving)
    else:
        return 0
    

def _display_court_name(canvas, x: int , y: int, court_name: str, match_status=None):
    font = FONT_SIGNAGE_COURT_NAME
    w_bg = W_MATCH - 1
    h_bg = h_font_court_name + 2
    fill_rect(canvas, x, y, w_bg, h_bg, COLOR_COURT_NAME_BG)    
    
    x_court_name = x + 1
    y_court_name = y + h_font_court_name + 1
    draw_text(canvas, x_court_name, y_court_name, court_name, font, COLOR_COURT_NAME)

    if match_status is not None:
        # Display starting time
        x_time = x + (W_MATCH - width_in_pixels(font, match_status)) - 1
        y_time = y_court_name
        draw_text(canvas, x_time, y_time, match_status, font, COLOR_MATCH_STATUS)

    return h_bg

def draw_tournament(canvas, signage_info):
    #clear canvas
    fill_rect(canvas, 0, 0, W_PANEL, H_PANEL, COLOR_MATCH_BG)

    for court_pos, court in enumerate(signage_info.get('courts', [])):
        court_name = court.get('name', 'Court ' + str(court_pos + 1))
        team1 = court.get('team1')
        team2 = court.get('team2')
        score_sets = court.get('score-sets')
        score_game = court.get('score-game')
        is_serving_t1 = court.get('is-serving-t1')
        match_status = court.get('match-status')

        _display_match(canvas, court_pos, court_name, team1, team2, score_sets, score_game, is_serving_t1, match_status)


def _display_match(canvas, court_pos: int , court_name: str, 
                          team1, team2,
                          score_sets: List[int], score_game: List[str], is_serving_t1:bool, 
                          match_status=None):
    x0, y0 = _match_coordinates(court_pos)

    fill_rect(canvas, x0, y0, W_MATCH, H_MATCH, COLOR_MATCH_BG)

    # 1. Court name    
    x_court_name = x0
    y_court_name = y0
    y_shift = _display_court_name(canvas, x_court_name, y_court_name, court_name, match_status)
    
    
    
    # 2. Teams
    
    score_sets_t1 = []
    score_sets_t2 = []
    for ss in score_sets or []:
        is_finished = True # TODO handle match finished state        
        colors = score_colors(ss[0], ss[1], is_finished)

        score_sets_t1.append((ss[0], colors[0]))        
        score_sets_t2.append((ss[1], colors[1]))

    ## 2.1 Team 1    
    score_game_t1 = str(score_game[0]) if score_game else ""
    y_t1 = y0 + y_shift + 2
    y_shift = _display_team(canvas, x0, y_t1, team1, score_sets_t1, is_serving_t1, score_game_t1)

    ## 2.2 Team 2
    score_game_t2 = str(score_game[1]) if score_game else ""
    y_t2 = y_t1 + y_shift
    is_serving_t2 = None if is_serving_t1 is None else not(is_serving_t1)
    _display_team(canvas, x0, y_t2, team2, score_sets_t2, is_serving_t2, score_game_t2)

    
