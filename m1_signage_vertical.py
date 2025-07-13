# Vertical signage for arbitrary tournament (e.g. ITF, etc.)
# Displays up to 4 matches / courts simultaneously

from sevencourts import *
from m1_signage import *
import time
import m1_scoreboard

COLOR_TOURNAMENT_NAME = COLOR_WHITE
COLOR_TOURNAMENT_NAME_BG = COLOR_BW_VAIHINGEN_ROHR_BLUE
COLOR_COURT_SEPARATOR_LINE = COLOR_GREY_DARK
COLOR_COURT_NAME = COLOR_BLACK
COLOR_COURT_NAME_BG = COLOR_GREY
COLOR_TEAM_NAME = COLOR_WHITE

IMAGES_SPONSOR_LOGOS = ["images/logos/ITF/ITF_64x32_white_bg.png",
                        "images/logos/TC BW Vaihingen-Rohr/tc-bw-vaihingen-rohr-64x32.png",
                        "images/logos/7C/sevencourts_7c_64x32.png"]
PERIOD_SPONSOR_FRAME_S = 15  # seconds

X_SET1 = 48
X_SET2 = 54
X_SET3 = 60

def draw_signage_itftournament(canvas, courts, tournament_name = "Welcome!"):
    # XXX the panel must be started in VERTICAL mode (./m1_vertical.sh)
    # s.https://suprematic.slack.com/archives/DF1LE3XLY/p1719413956323839
    
    draw_tournament_title(canvas, tournament_name)

    court_index = 1
    for court in courts:
        court_name = court.get("court-name")
        match = court.get("match")
        if match:
            t1_set1 = t2_set1 = t1_set2 = t2_set2 = t1_set3 = t2_set3 = None
            set_scores = match["set-scores"] or []
            if len(set_scores) == 1:
                t1_set1 = set_scores[0][0]
                t2_set1 = set_scores[0][1]
            elif len(set_scores) == 2:
                t1_set1 = set_scores[0][0]
                t2_set1 = set_scores[0][1]
                t1_set2 = set_scores[1][0]
                t2_set2 = set_scores[1][1]
            elif len(set_scores) == 3:
                t1_set1 = set_scores[0][0]
                t2_set1 = set_scores[0][1]
                t1_set2 = set_scores[1][0]
                t2_set2 = set_scores[1][1]
                t1_set3 = set_scores[2][0]
                t2_set3 = set_scores[2][1]
            t1 = match.get("team1")
            t2 = match.get("team2")
            if match.get("isDoubles"):
                t1p1name = t1.get("player1").get("name")
                t1p2name = t1.get("player2").get("name")
                t2p1name = t2.get("player1").get("name")
                t2p2name = t2.get("player2").get("name")
                t1p1flag = t1.get("player1").get("flag")
                t1p2flag = t1.get("player2").get("flag")
                t2p1flag = t2.get("player1").get("flag")
                t2p2flag = t2.get("player2").get("flag")
                draw_signage_match_doubles([court_index, court_name],
                                    [[t1p1name, t1p1flag], [t1p2name, t1p2flag]],
                                    [[t2p1name, t2p1flag], [t2p2name, t2p2flag]],
                                    set_scores)
            else:

                t1_name = t1.get("name").split(",")[0]  # FIXME remove it when data is properly set
                t1_flag = t1.get("flag")
                t2_name = t2.get("name").split(",")[0]  # FIXME remove it when data is properly set
                t2_flag = t2.get("flag")
                draw_signage_match_singles(court_index, court_name, t1_name, t2_name, t1_flag, t2_flag,
                                                t1_set1, t2_set1, t1_set2, t2_set2, t1_set3, t2_set3)
        else:
            draw_signage_match_singles(court_index, court_name, "", "")
        court_index += 1

    # UI test data
    # self.draw_signage_match_singles(1, "1.Stuttgart", "Clementenko", "Jurikova", "germany", "serbia", 1, 6, 6, 2, 3, 4)
    # self.draw_signage_match_singles(2, "2.Brunold Auto", "Seiboldenko", "Schädel", "germany", "germany", 6, 3, 2, 2)
    # self.draw_signage_match_singles(3, "3.Lapp", "Köläkäiüißenko", "Kling", "japan", "switzerland", 2, 0)
    # self.draw_signage_match_singles(4, "4.Egeler", "Mikulslytenko", "Radovanovic", "lithuania", "croatia")

    # self.draw_signage_match_doubles([1, "1. Stuttgart"],
    #                                [["Mikulslytenko", "ukraine"], ["Azarenka", "belarus"]],
    #                                [["Radovanovic", "serbia"], ["Dapkunaite", "lithuania"]],
    #                                [[1, 6], [6, 2], [3, 4]])

    draw_signage_tournament_sponsors(canvas)

def draw_signage_court_name(canvas, x: int, y0: int, court_name):
    y = y0
    graphics.DrawLine(canvas, x, y, W_PANEL, y, COLOR_COURT_SEPARATOR_LINE)
    y += 1
    fill_rect(canvas, x, y, 64, 1 + H_FONT_XXS + 1, COLOR_COURT_NAME_BG)
    y += H_FONT_XXS + 1
    graphics.DrawText(canvas, FONT_XXS, x + 1, y, COLOR_COURT_NAME, court_name or '')
    y += 1
    graphics.DrawLine(canvas, x, y, W_PANEL, y, COLOR_COURT_SEPARATOR_LINE)
    y += 1
    return y - y0  # 9

def draw_signage_match_team(canvas, x0: int, y0: int, team_name, team_flag,
                            score_set1, color_set1, score_set2, color_set2, score_set3, color_set3):
    y = y0
    if team_flag:
        w_flag = W_FLAG_SMALL
        x_name = x0 + W_FLAG_SMALL + 1        
        draw_flag(canvas, team_flag, x0, y)
    else:
        w_flag = 0
        x_name = x0

    y += H_FONT_XS
    w_name_max = W_TILE - w_flag
    if score_set3 is not None:
        w_name_max = X_SET1 - 2 - w_flag
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET1, y, color_set1, str(score_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, color_set2, str(score_set2))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, color_set3, str(score_set3))
    elif score_set2 is not None:
        w_name_max = X_SET2 - 2 - w_flag
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, color_set1, str(score_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, color_set2, str(score_set2))
    elif score_set1 is not None:
        w_name_max = X_SET3 - 2 - w_flag
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, color_set1, str(score_set1))

    team_name_truncated = truncate_text(FONT_XS, w_name_max, team_name)
    graphics.DrawText(canvas, FONT_XS, x_name, y, COLOR_TEAM_NAME, team_name_truncated)

def draw_signage_match_team_flags(canvas, x0: int, y0: int, p1flag, p2flag,
                                    score_set1, color_set1, score_set2, color_set2, score_set3, color_set3):
    y = y0
    x = x0 + 7
    draw_flag(canvas, p1flag, x, y)
    x += W_FLAG_SMALL + 12
    draw_flag(canvas, p2flag, x, y)
    y += H_FONT_XS
    x = x0 + 7 + W_FLAG_SMALL + 4
    graphics.DrawText(canvas, FONT_XS, x, y, COLOR_TEAM_NAME, "/")
    if score_set3 is not None:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET1, y, color_set1, str(score_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, color_set2, str(score_set2))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, color_set3, str(score_set3))
    elif score_set2 is not None:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, color_set1, str(score_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, color_set2, str(score_set2))
    elif score_set1 is not None:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, color_set1, str(score_set1))

def draw_signage_match_singles(canvas, court_index: int, court_name, t1_name, t2_name, t1_flag=None, t2_flag=None,
                                t1_set1=None, t2_set1=None, t1_set2=None, t2_set2=None, t1_set3=None, t2_set3=None):

    color_set1 = color_set2 = color_set3 = [None, None]
    if t1_set3 is not None:
        color_set1 = score_colors(t1_set1, t2_set1)
        color_set2 = score_colors(t1_set2, t2_set2)
        color_set3 = score_colors(t1_set3, t2_set3, False)
    elif t1_set2 is not None:
        color_set1 = score_colors(t1_set1, t2_set1)
        color_set2 = score_colors(t1_set2, t2_set2, False)
    elif t1_set1 is not None:
        color_set1 = score_colors(t1_set1, t2_set1, False)

    y0 = 32 * court_index if ORIENTATION_VERTICAL else (0 if court_index % 2 else H_TILE)
    x0 = 0 if ORIENTATION_VERTICAL else (W_TILE if court_index < 3 else W_TILE * 2)

    h_court_name = draw_signage_court_name(canvas, x0, y0, court_name)

    y = y0 + h_court_name + 4

    draw_signage_match_team(canvas, x0, y, t1_name, t1_flag,
                                    t1_set1, color_set1[0],
                                    t1_set2, color_set2[0],
                                    t1_set3, color_set3[0])

    y += 9

    draw_signage_match_team(canvas, x0, y, t2_name, t2_flag,
                                    t2_set1, color_set1[1],
                                    t2_set2, color_set2[1],
                                    t2_set3, color_set3[1])

def draw_signage_match_doubles(canvas, court, t1, t2, score):

    court_index = court[0]
    court_name = court[1]

    t1p1name = t1[0][0]
    t1p1flag = t1[0][1]
    t1p2name = t1[1][0]
    t1p2flag = t1[1][1]
    t2p1name = t2[0][0]
    t2p1flag = t2[0][1]
    t2p2name = t2[1][0]
    t2p2flag = t2[1][1]

    t1_set1 = t2_set1 = t1_set2 = t2_set2 = t1_set3 = t2_set3 = None
    set_scores = score or []
    if len(set_scores) == 1:
        t1_set1 = set_scores[0][0]
        t2_set1 = set_scores[0][1]
    elif len(set_scores) == 2:
        t1_set1 = set_scores[0][0]
        t2_set1 = set_scores[0][1]
        t1_set2 = set_scores[1][0]
        t2_set2 = set_scores[1][1]
    elif len(set_scores) == 3:
        t1_set1 = set_scores[0][0]
        t2_set1 = set_scores[0][1]
        t1_set2 = set_scores[1][0]
        t2_set2 = set_scores[1][1]
        t1_set3 = set_scores[2][0]
        t2_set3 = set_scores[2][1]

    color_set1 = color_set2 = color_set3 = [None, None]
    if t1_set3 is not None:
        color_set1 = score_colors(t1_set1, t2_set1)
        color_set2 = score_colors(t1_set2, t2_set2)
        color_set3 = score_colors(t1_set3, t2_set3, False)
    elif t1_set2 is not None:
        color_set1 = score_colors(t1_set1, t2_set1)
        color_set2 = score_colors(t1_set2, t2_set2, False)
    elif t1_set1 is not None:
        color_set1 = score_colors(t1_set1, t2_set1, False)

    y0 = 32 * court_index if ORIENTATION_VERTICAL else (0 if court_index % 2 else H_TILE)
    x0 = 0 if ORIENTATION_VERTICAL else (W_TILE if court_index < 3 else W_TILE * 2)

    h_court_name = draw_signage_court_name(canvas, x0, y0, court_name)

    y = y0 + h_court_name + 4

    seconds_now = int(time.time())
    seconds_passed = seconds_now - SECONDS_START
    PERIOD_DOUBLES_FRAME_S = 4 # seconds

    if (seconds_passed // PERIOD_DOUBLES_FRAME_S) % 2:
        # draw names

        t1_name = t1p1name[:4] + "/" + t1p2name[:4]
        t2_name = t2p1name[:4] + "/" + t2p2name[:4]

        draw_signage_match_team(canvas, x0, y, t1_name, None,
                                        t1_set1, color_set1[0],
                                        t1_set2, color_set2[0],
                                        t1_set3, color_set3[0])

        y += 9

        draw_signage_match_team(canvas, x0, y, t2_name, None,
                                        t2_set1, color_set1[1],
                                        t2_set2, color_set2[1],
                                        t2_set3, color_set3[1])
    else:
        # draw flags
        draw_signage_match_team_flags(canvas, x0, y, t1p1flag, t1p2flag,
                                        t1_set1, color_set1[0],
                                        t1_set2, color_set2[0],
                                        t1_set3, color_set3[0])

        y += 9

        draw_signage_match_team_flags(canvas, x0, y, t2p1flag, t2p2flag,
                                            t1_set1, color_set1[0],
                                            t1_set2, color_set2[0],
                                            t1_set3, color_set3[0])

def draw_tournament_title(canvas, title):
    fill_rect(canvas, 0, 0, W_TILE, H_TILE, COLOR_TOURNAMENT_NAME_BG)
    font = FONT_S
    lines = title.split(" ", 1)
    y = y_font_center(font, H_TILE / len(lines))
    for line in lines:
        x = x_font_center(line, W_TILE, font)
        graphics.DrawText(canvas, font, x, y, COLOR_TOURNAMENT_NAME, line)
        y += font.height

def draw_signage_tournament_sponsors(canvas):

    seconds_now = int(time.time())
    seconds_passed = seconds_now - SECONDS_START
    sponsor_index = (seconds_passed // PERIOD_SPONSOR_FRAME_S) % len(IMAGES_SPONSOR_LOGOS)

    file_image = IMAGES_SPONSOR_LOGOS[sponsor_index]
    x = 0
    y = H_PANEL - H_TILE
    canvas.SetImage(Image.open(file_image).convert('RGB'), x, y)
