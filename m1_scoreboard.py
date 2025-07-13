from sevencourts import *

GAME_SCORES = ('15', '30', '40', 'A')

# Scoreboard styles
COLOR_SCORE_SET = COLOR_WHITE
COLOR_SCORE_SET_WON = COLOR_SCORE_SET
COLOR_SCORE_SET_LOST = COLOR_GREY
COLOR_SCORE_GAME = COLOR_WHITE
COLOR_SCORE_SERVICE = COLOR_YELLOW
COLOR_TEAM_NAME = COLOR_WHITE
COLOR_SCORE_BACKGROUND = COLOR_BLACK
FONT_TEAM_NAME_XL = FONT_XL
FONT_TEAM_NAME_L = FONT_L
FONT_TEAM_NAME_M = FONT_M
FONT_TEAM_NAME_S = FONT_S
if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    FONT_SCORE = FONT_L
else:
    FONT_SCORE = FONT_XL_SDK

UPPER_CASE_NAMES = True
MARGIN_NAMES_SCOREBOARD = 3

X_MIN_SCOREBOARD = int(W_PANEL / 2)
W_SCORE_SET = 20
X_SCORE_GAME = 163
X_SCORE_SERVICE = 155

def _player_name(p, noname="Noname"):
    return p["lastname"] or p["firstname"] or noname

def _display_set_digit(canvas, x, y, font, color, score):
    # FIXME meh
    if score != "":
        if int(score) < 10:
            graphics.DrawText(canvas, font, x, y, color, str(score))
        else:
            score = str(int(score) % 10)
            fill_rect(canvas, x - 2, y + 1, width_in_pixels(font, score) + 2, -y_font_offset(font) - 3, color)
            graphics.DrawText(canvas, font, x, y, COLOR_BLACK, score)

def _display_score(canvas, match):
    t1_on_serve=match["team1"]["serves"]
    t2_on_serve=match["team2"]["serves"]
    number_of_sets = len(match["team1"]["setScores"] or [])
    is_match_over = match["matchResult"] in ('T1_WON', 'T2_WON', 'DRAW')
    t1_game = match["team1"].get("gameScore", "")
    t2_game = match["team2"].get("gameScore", "")
    t1_game = str(t1_game if t1_game is not None else "")
    t2_game = str(t2_game if t2_game is not None else "")

    if number_of_sets == 0:
        t1_set1 = t2_set1 = t1_set2 = t2_set2 = t1_set3 = t2_set3 = ""
        c_t1_set1 = c_t2_set1 = c_t1_set2 = c_t2_set2 = c_t1_set3 = c_t2_set3 = COLOR_BLACK
        x_set1 = x_set2 = x_set3 = W_PANEL
    elif number_of_sets == 1:
        t1_set1 = match["team1"]["setScores"][0]
        t2_set1 = match["team2"]["setScores"][0]
        t1_set2 = t2_set2 = t1_set3 = t2_set3 = ""
        if is_match_over:
            c_t1_set1 = COLOR_SCORE_SET_WON if t1_set1 > t2_set1 else COLOR_SCORE_SET_LOST
            c_t2_set1 = COLOR_SCORE_SET_WON if t2_set1 > t1_set1 else COLOR_SCORE_SET_LOST
        else:
            c_t1_set1 = c_t2_set1 = COLOR_SCORE_SET
        c_t1_set2 = c_t2_set2 = c_t1_set3 = c_t2_set3 = COLOR_BLACK
        x_set1 = X_MIN_SCOREBOARD + W_SCORE_SET + W_SCORE_SET
        x_set2 = x_set3 = W_PANEL
    elif number_of_sets == 2:
        t1_set1 = match["team1"]["setScores"][0]
        t2_set1 = match["team2"]["setScores"][0]
        t1_set2 = match["team1"]["setScores"][1]
        t2_set2 = match["team2"]["setScores"][1]
        t1_set3 = t2_set3 = ""
        c_t1_set1 = COLOR_SCORE_SET_WON if t1_set1 > t2_set1 else COLOR_SCORE_SET_LOST
        c_t2_set1 = COLOR_SCORE_SET_WON if t2_set1 > t1_set1 else COLOR_SCORE_SET_LOST
        if is_match_over:
            c_t1_set2 = COLOR_SCORE_SET_WON if t1_set2 > t2_set2 else COLOR_SCORE_SET_LOST
            c_t2_set2 = COLOR_SCORE_SET_WON if t2_set2 > t1_set2 else COLOR_SCORE_SET_LOST
        else:
            c_t1_set2 = c_t2_set2 = COLOR_SCORE_SET
        c_t1_set3 = c_t2_set3 = COLOR_BLACK
        x_set1 = X_MIN_SCOREBOARD + W_SCORE_SET
        x_set2 = x_set1 + W_SCORE_SET
        x_set3 = W_PANEL
    else:  # (number_of_sets ==3) -- 4+ sets are not supported yet
        t1_set1 = match["team1"]["setScores"][0]
        t2_set1 = match["team2"]["setScores"][0]
        t1_set2 = match["team1"]["setScores"][1]
        t2_set2 = match["team2"]["setScores"][1]
        t1_set3 = match["team1"]["setScores"][2]
        t2_set3 = match["team2"]["setScores"][2]
        c_t1_set1 = COLOR_SCORE_SET_WON if t1_set1 > t2_set1 else COLOR_SCORE_SET_LOST
        c_t2_set1 = COLOR_SCORE_SET_WON if t2_set1 > t1_set1 else COLOR_SCORE_SET_LOST
        c_t1_set2 = COLOR_SCORE_SET_WON if t1_set2 > t2_set2 else COLOR_SCORE_SET_LOST
        c_t2_set2 = COLOR_SCORE_SET_WON if t2_set2 > t1_set2 else COLOR_SCORE_SET_LOST
        if is_match_over:
            c_t1_set3 = COLOR_SCORE_SET_WON if t1_set3 > t2_set3 else COLOR_SCORE_SET_LOST
            c_t2_set3 = COLOR_SCORE_SET_WON if t2_set3 > t1_set3 else COLOR_SCORE_SET_LOST

            # A crutch fix to nicely display match-tie-break result.
            # FIXME Match/score metadata is missing to do it properly.
            is_mtb = t1_set3 >= 10 or t2_set3 >= 10
            if is_mtb:
                t1_game = str(t1_set3)
                t2_game = str(t2_set3)
                t1_set3 = t1_set2
                t2_set3 = t2_set2
                t1_set2 = t1_set1
                t2_set2 = t2_set1
                t1_set1 = ""
                t2_set1 = ""

        else:
            c_t1_set3 = c_t2_set3 = COLOR_SCORE_SET

            # FIXME  meh, this will not work when score in MTB will be 15 what is rare but not excluded
            # FIXME Match/score metadata is missing to do it properly.
            is_mtb = t1_set3 == 0 and t2_set3 == 0 and t1_game not in GAME_SCORES and t2_game not in GAME_SCORES
            if is_mtb:
                t1_set3 = t1_set2
                t2_set3 = t2_set2
                t1_set2 = t1_set1
                t2_set2 = t2_set1
                t1_set1 = ""
                t2_set1 = ""

        x_set1 = X_MIN_SCOREBOARD
        x_set2 = x_set1 + W_SCORE_SET
        x_set3 = x_set2 + W_SCORE_SET

    # center score digits
    y_t1 = y_font_center(FONT_SCORE, H_PANEL / 2)
    y_t2 = y_t1 + (H_PANEL / 2)

    # "cover" the score area so that names do not intersect
    x_score = min(x_set1, X_SCORE_SERVICE) - MARGIN_NAMES_SCOREBOARD
    fill_rect(canvas, x_score, 0, W_PANEL - x_score, H_PANEL, COLOR_SCORE_BACKGROUND)

    x_t1_score_game = X_SCORE_GAME if len(t1_game) != 1 else X_SCORE_GAME + 8
    x_t2_score_game = X_SCORE_GAME if len(t2_game) != 1 else X_SCORE_GAME + 8

    # Americano
    if not match.get("isTotalPointsMatch", False):
        _display_set_digit(canvas, x_set1, y_t1, FONT_SCORE, c_t1_set1, t1_set1)
        _display_set_digit(canvas, x_set2, y_t1, FONT_SCORE, c_t1_set2, t1_set2)
        _display_set_digit(canvas, x_set3, y_t1, FONT_SCORE, c_t1_set3, t1_set3)

        _display_set_digit(canvas, x_set1, y_t2, FONT_SCORE, c_t2_set1, t2_set1)
        _display_set_digit(canvas, x_set2, y_t2, FONT_SCORE, c_t2_set2, t2_set2)
        _display_set_digit(canvas, x_set3, y_t2, FONT_SCORE, c_t2_set3, t2_set3)

    # FIXME Test if this works for finished e.g. tie-break matches
    if not is_match_over:
        graphics.DrawText(canvas, FONT_SCORE, x_t1_score_game, y_t1, COLOR_SCORE_GAME, t1_game)
        graphics.DrawText(canvas, FONT_SCORE, x_t2_score_game, y_t2, COLOR_SCORE_GAME, t2_game)

    # service indicator
    if not match.get("hideServiceIndicator", False) and not is_match_over:
        b = (0, 0, 0)
        y = (255, 255, 0)
        ball = [
            [b, b, y, y, y, b, b],
            [b, y, y, y, y, y, b],
            [y, y, y, y, y, y, y],
            [y, y, y, y, y, y, y],
            [y, y, y, y, y, y, y],
            [b, y, y, y, y, y, b],
            [b, b, y, y, y, b, b]]
        y_service_t1 = int(H_PANEL / 2 / 2 - len(ball) / 2)
        y_service_t2 = y_service_t1 + H_PANEL / 2
        if t1_on_serve:
            draw_matrix(canvas, ball, X_SCORE_SERVICE, y_service_t1)
        elif t2_on_serve:
            draw_matrix(canvas, ball, X_SCORE_SERVICE, y_service_t2)

def _display_names(canvas, match):

    ios_teca_client_v1_1_27 = match["team1"]["p1"] is None and match["team2"]["p1"] is None

    # 1. flags
    if ios_teca_client_v1_1_27:
        t1p1_flag = t2p1_flag = t1p2_flag = t2p2_flag = ''
    else:
        t1p1_flag = match["team1"]["p1"]["flag"]
        t2p1_flag = match["team2"]["p1"]["flag"]
        if match["isDoubles"]:
            t1p2_flag = match["team1"]["p2"]["flag"]
            t2p2_flag = match["team2"]["p2"]["flag"]
        else:
            t1p2_flag = t2p2_flag = ''

    t1p1_flag_len = 0 if t1p1_flag is None else len(t1p1_flag)
    t1p2_flag_len = 0 if t1p2_flag is None else len(t1p2_flag)
    t2p1_flag_len = 0 if t2p1_flag is None else len(t2p1_flag)
    t2p2_flag_len = 0 if t2p2_flag is None else len(t2p2_flag)

    display_flags = max(t1p1_flag_len, t1p2_flag_len, t2p1_flag_len, t2p2_flag_len) > 0
    same_flags_in_teams = (t1p1_flag == t1p2_flag) & (t2p1_flag == t2p2_flag)
    if display_flags:
        t1p1_flag = None if not t1p1_flag else load_flag_image(t1p1_flag)
        t1p2_flag = None if not t1p2_flag else load_flag_image(t1p2_flag)
        t2p1_flag = None if not t2p1_flag else load_flag_image(t2p1_flag)
        t2p2_flag = None if not t2p2_flag else load_flag_image(t2p2_flag)
        flag_width = W_FLAG
    else:
        flag_width = 0

    # 2. names
    t1_set_scores = match["team1"]["setScores"] or []
    t2_set_scores = match["team2"]["setScores"] or []
    if (len(t1_set_scores)==0):
        x_scoreboard = X_SCORE_SERVICE
    elif len(t1_set_scores) == 1:
        x_scoreboard = X_MIN_SCOREBOARD + W_SCORE_SET + W_SCORE_SET
    elif len(t1_set_scores) == 2:
        x_scoreboard = X_MIN_SCOREBOARD + W_SCORE_SET
    else:  # (len(t1_set_scores)==3) -- 4+ sets are not supported yet
        x_scoreboard = X_MIN_SCOREBOARD
    name_max_width = x_scoreboard - flag_width - 1 - MARGIN_NAMES_SCOREBOARD

    t1p1 = t1p2 = t2p1 = t2p2 = ""

    if ios_teca_client_v1_1_27:
        t1p1 = match["team1"]["name"]
        t2p1 = match["team2"]["name"]
        t1p2 = t2p2 = ''
    elif match["isTeamEvent"] or not match["isDoubles"]:
        if match["isTeamEvent"]:
            t1p1 = match["team1"]["name"]
            t2p1 = match["team2"]["name"]
        else:
            t1p1 = _player_name(match["team1"]["p1"], "Player1")
            t2p1 = _player_name(match["team2"]["p1"], "Player2")
        t1p2 = t2p2 = ''
    elif match["isDoubles"]:
        t1p1 = _player_name(match["team1"]["p1"], "Player1")
        t1p2 = _player_name(match["team1"]["p2"], "Player2")
        t2p1 = _player_name(match["team2"]["p1"], "Player3")
        t2p2 = _player_name(match["team2"]["p2"], "Player4")

    if UPPER_CASE_NAMES:
        t1p1 = t1p1.upper()
        t1p2 = t1p2.upper()
        t2p1 = t2p1.upper()
        t2p2 = t2p2.upper()

    x = flag_width + 2
    if match["isTeamEvent"] or not match["isDoubles"]:
        name_max_height = int(H_PANEL / 2 - 2)  # =>30
        font = pick_font_that_fits(name_max_width, name_max_height, t1p1, t2p1)
        y_t1 = y_font_center(font, H_PANEL / 2)
        y_t2 = y_t1 + H_PANEL / 2
        graphics.DrawText(canvas, font, x, y_t1, COLOR_TEAM_NAME, t1p1)
        graphics.DrawText(canvas, font, x, y_t2, COLOR_TEAM_NAME, t2p1)
        if display_flags:
            _display_singles_flags(canvas, t1p1_flag, t2p1_flag)

    elif match["isDoubles"]:
        # (FLAG)
        # 2 (12) 3 (12) 3 3 (12) 3 (12) 2
        # 9    (12)    11 10    (12)    10
        # (NAME)
        # 1 (14) 1 (14) 2 2 (14) 1 (14) 1

        name_max_height = 1 + H_FLAG + 1  # => 14

        font = pick_font_that_fits(name_max_width, name_max_height, t1p1, t1p2, t2p1, t2p2)

        y_offset = y_font_center(font, name_max_height)

        y_t1p1 = 1 + y_offset
        y_t1p2 = 1 + name_max_height + 1 + y_offset
        y_t2p1 = 1 + name_max_height + 1 + name_max_height + 2 + 2 + y_offset
        y_t2p2 = 1 + name_max_height + 1 + name_max_height + 2 + 2 + name_max_height + 1 + y_offset
        graphics.DrawText(canvas, font, x, y_t1p1, COLOR_TEAM_NAME, t1p1)
        graphics.DrawText(canvas, font, x, y_t1p2, COLOR_TEAM_NAME, t1p2)
        graphics.DrawText(canvas, font, x, y_t2p1, COLOR_TEAM_NAME, t2p1)
        graphics.DrawText(canvas, font, x, y_t2p2, COLOR_TEAM_NAME, t2p2)
        if display_flags:
            if same_flags_in_teams:
                _display_singles_flags(canvas, t1p1_flag, t2p1_flag)
            else:
                # 2 (12) 3 (12) 3 3 (12) 3 (12) 2
                y_flag_t1p1 = 2
                y_flag_t1p2 = y_flag_t1p1 + H_FLAG + 3
                y_flag_t2p1 = y_flag_t1p2 + H_FLAG + 3 + 3
                y_flag_t2p2 = y_flag_t2p1 + H_FLAG + 3

                if t1p1_flag is not None:
                    canvas.SetImage(t1p1_flag, 0, y_flag_t1p1)

                if t1p2_flag is not None:
                    canvas.SetImage(t1p2_flag, 0, y_flag_t1p2)

                if t2p1_flag is not None:
                    canvas.SetImage(t2p1_flag, 0, y_flag_t2p1)

                if t2p2_flag is not None:
                    canvas.SetImage(t2p2_flag, 0, y_flag_t2p2)

def _display_singles_flags(canvas, img_t1, img_t2):
    if img_t1 is not None:
        y_flag_t1 = max(0, H_PANEL / 2 / 2 - img_t1.height / 2)
        canvas.SetImage(img_t1, 0, y_flag_t1)

    if img_t2 is not None:
        y_flag_t2 = max(H_PANEL / 2, H_PANEL / 2 + H_PANEL / 2 / 2 - img_t2.height / 2)
        canvas.SetImage(img_t2, 0, y_flag_t2)

def _display_winner(canvas, match):
    # FIXME winner is not displayed
    b = (0, 0, 0)
    y = (255, 215, 0)
    w = (96, 64, 0)
    cup = [
        [b, b, y, y, y, y, y, b, b],
        [w, y, y, y, y, y, y, y, w],
        [w, b, y, y, y, y, y, b, w],
        [w, b, y, y, y, y, y, b, w],
        [b, w, y, y, y, y, y, w, b],
        [b, b, w, y, y, y, w, b, b],
        [b, b, b, y, y, y, b, b, b],
        [b, b, b, b, y, b, b, b, b],
        [b, b, y, y, y, y, y, b, b],
        [b, b, y, y, y, y, y, b, b]]
    match_result = match.get("matchResult", None)
    medal_delta = 12
    x_medal = X_SCORE_SERVICE
    if match_result == "T1_WON":
        draw_matrix(canvas, cup, x_medal, medal_delta)
    elif match_result == "T2_WON":
        draw_matrix(canvas, cup, x_medal, H_PANEL / 2 + medal_delta)

def draw_match(canvas, panel_info):
    _display_names(canvas, panel_info)
    _display_score(canvas, panel_info)
    _display_winner(canvas, panel_info)
