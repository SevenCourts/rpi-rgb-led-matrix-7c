#!/usr/bin/env python3

import os

from sevencourts import W_PANEL

# Set the environment variable USE_RGB_MATRIX_EMULATOR to use with
# emulator https://github.com/ty-porter/RGBMatrixEmulator
# Do not set to use with real SDK https://github.com/hzeller/rpi-rgb-led-matrix
if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    from RGBMatrixEmulator import graphics
else:
    from rgbmatrix import graphics

from samplebase import SampleBase
from sevencourts import *
import time
import urllib.request
from urllib.error import URLError
from datetime import datetime
from PIL import Image
import json
import socket
import logging
import requests
import subprocess
from datetime import datetime, timedelta
from dateutil import parser
from dateutil import tz

SECONDS_START = int(time.time())

GIT_COMMIT_ID = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()

# FIXME use not hardcoded directory (TBD)
IMAGE_CACHE_DIR = "/opt/7c/cache-images"
os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
# The default 0o777 does not work,
# see https://stackoverflow.com/questions/5231901/permission-problems-when-creating-a-dir-with-os-makedirs-in-python
os.chmod(IMAGE_CACHE_DIR, 0o777)

PANEL_CONFIG = os.getenv('PANEL_CONFIG')

LATEST_IDLE_MODE_IMAGE_PATH = IMAGE_CACHE_DIR + '/latest_idle_image'

PANEL_NAME = socket.gethostname()

BASE_URL = os.getenv('TABLEAU_SERVER_BASE_URL', 'https://prod.tableau.tennismath.com')

REGISTRATION_URL = BASE_URL + "/panels/"

PANEL_ID = os.getenv('TABLEAU_PANEL_ID')

GAME_SCORES = ('15', '30', '40', 'A')

# Style constants

# Style sheet

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
    FONT_CLOCK = FONT_L if ORIENTATION_HORIZONTAL else FONT_M
    FONT_SCORE = FONT_L
else:
    FONT_CLOCK = FONTS_V0[0] if ORIENTATION_HORIZONTAL else FONT_M
    FONT_SCORE = FONTS_V0[0]

FONT_CLOCK_S_1=FONT_L_7SEGMENT
FONT_CLOCK_M_1=FONT_XL_7SEGMENT
FONT_CLOCK_L_1=FONT_XXL_7SEGMENT

FONT_CLOCK_S_2=FONT_L_SPLEEN
FONT_CLOCK_M_2=FONT_XL_SPLEEN
FONT_CLOCK_L_2=FONT_XXL_SPLEEN

FONT_BOOKING = FONT_S

COLOR_BOOKING_GREETING = COLOR_7C_BLUE
COLOR_CLOCK = COLOR_GREY
COLOR_CLOCK_STANDBY = COLOR_GREY_DARKEST

UPPER_CASE_NAMES = True
MARGIN_NAMES_SCOREBOARD = 3

X_MIN_SCOREBOARD = int(W_PANEL / 2)
W_SCORE_SET = 20
X_SCORE_GAME = 163
X_SCORE_SERVICE = 155

W_CLOCK_OVERLAY = 74 # right from logo
W_LOGO_WITH_CLOCK = 122 # left from clock

__COLOR_BW_VAIHINGEN_ROHR_BLUE = graphics.Color(0x09, 0x65, 0xA6)  # #0965A6

COLOR_SIGNAGE_BG_TOURNAMENT_NAME = __COLOR_BW_VAIHINGEN_ROHR_BLUE
COLOR_SIGNAGE_FG_TOURNAMENT_NAME = COLOR_WHITE

COLOR_SIGNAGE_FG_COURT_SEPARATOR_LINE = COLOR_GREY_DARK
COLOR_SIGNAGE_BG_COURT_NAME = COLOR_GREY
COLOR_SIGNAGE_FG_COURT_NAME = COLOR_BLACK

COLOR_SIGNAGE_FG_TEAM_NAME = COLOR_WHITE
COLOR_SIGNAGE_FG_SCORE = COLOR_GREY
COLOR_SIGNAGE_FG_SCORE_WON = COLOR_WHITE
COLOR_SIGNAGE_FG_SCORE_LOST = COLOR_GREY

X_SET1 = 48
X_SET2 = 54
X_SET3 = 60

IMAGES_SPONSOR_LOGOS = ["images/logos/ITF/ITF_64x32_white_bg.png",
                        "images/logos/TC BW Vaihingen-Rohr/tc-bw-vaihingen-rohr-64x32.png",
                        "images/logos/7C/sevencourts_7c_64x32.png"]
PERIOD_SPONSOR_FRAME_S = 15  # seconds

BOOKIN_OVERLAP_MINUTES = 10

def panel_info_url(panel_id):
    return BASE_URL + "/panels/" + panel_id + "/match"


def uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            return float(f.readline().split()[0])
    except Exception as ex:
        log(ex, 'Cannot get uptime')
        return -1


# FIXME without this call, getting CPU temperature fails when is called from within class instance
# TODO wtf?!
try:
    from gpiozero import CPUTemperature

    print(CPUTemperature().temperature)
except Exception as e:
    log(e, 'Cannot get initial CPU temperature')


def cpu_temperature():
    try:
        from gpiozero import CPUTemperature
        return CPUTemperature().temperature
    except Exception as ex:
        log(ex, 'Cannot get CPU temperature')
        return -1


def register(url):
    data = json.dumps({"code": PANEL_NAME, "ip": ip_address(), "firmware_version": GIT_COMMIT_ID}).encode('utf-8')
    request = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(request, timeout=10) as response:
        j = json.loads(response.read().decode('utf-8'))
        log(url, "registered:", j)
        return j["id"]


def fetch_panel_info(panel_id):
    url = panel_info_url(panel_id)
    req = urllib.request.Request(url)
    req.add_header('7C-Is-Panel-Preview', 'false' if PANEL_ID is None else 'true')
    req.add_header('7C-Uptime', str(uptime()))
    req.add_header('7C-CPU-Temperature', str(cpu_temperature()))
    with urllib.request.urlopen(req, timeout=10) as response:
        log("url='" + url + "', status= " + str(response.status))
        if response.status == 200:
            match = json.loads(response.read().decode('utf-8'))
            log("match:", match)
            return match or None  # FIX: the server can return False if match is over, this leads to error then
        elif response.status == 205:
            idle_info = json.loads(response.read().decode('utf-8') or 'null')
            log("idle-info:", idle_info)
            return idle_info
    return None


def player_name(p, noname="Noname"):
    return p["lastname"] or p["firstname"] or noname


def thumbnail(image, w=W_PANEL, h=H_PANEL):
    # print ("original w: {0}, h: {1}".format(image.width, image.height))
    if image.width > w or image.height > h:
        image.thumbnail((w, h), Image.LANCZOS)
    # print ("result w: {0}, h: {1}".format(image.width, image.height))
    return image


def score_color(t1: int, t2: int, finished=True):
    if finished and t1 and t2:
        return [COLOR_SIGNAGE_FG_SCORE_WON if (t1 > t2) else COLOR_SIGNAGE_FG_SCORE_LOST,
                COLOR_SIGNAGE_FG_SCORE_WON if (t2 > t1) else COLOR_SIGNAGE_FG_SCORE_LOST]
    else:
        return [COLOR_SIGNAGE_FG_SCORE, COLOR_SIGNAGE_FG_SCORE]


def is_show_clock_with_image(image: Image):
    return ORIENTATION_VERTICAL or image.width < W_LOGO_WITH_CLOCK


def image_max_width(show_clock: bool):
    return W_PANEL if ORIENTATION_VERTICAL else W_LOGO_WITH_CLOCK if show_clock else W_PANEL


class SevenCourtsM1(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SevenCourtsM1, self).__init__(*args, **kwargs)
        self.last_known_club_mode = None
        self.last_known_club_mode_arg = None
        self.panel_info = {}
        self.panel_info_failed = False
        self.registration_failed = False
        self.read_startup_config()

    def read_startup_config(self):
        if PANEL_ID is None and PANEL_CONFIG is not None:
            startup_config = {}
            lines = []

            try:
                with open(PANEL_CONFIG, 'r') as file:
                    lines = list(filter(lambda x: len(x.strip()) > 0, file.read().splitlines()))
            except:
                pass

            if lines:
                startup_config = {k: v for k, v in map(lambda x: x.split('=', 1), lines)}

            k = 'ORIENTATION_VERTICAL'
            if k in startup_config:
                startup_config[k] = True

            self.startup_config = startup_config

    def write_startup_config(self):
        if PANEL_ID is None and PANEL_CONFIG is not None:
            startup_config = {}

            orientation = self.panel_info.get('orientation')
            if orientation == 'vertical':
                startup_config['ORIENTATION_VERTICAL'] = True

            if self.startup_config != startup_config:
                self.startup_config = startup_config
                conf = []
                for k, v in startup_config.items(): conf.append(k + '=' + str(v))

                try:
                    with open(PANEL_CONFIG, 'w') as file:
                        file.write('\n'.join(conf))
                except:
                    pass

    def run(self):
        self.canvas = self.matrix.CreateFrameCanvas()
        while True:
            panel_id = self.register()
            try:
                while True:
                    panel_info = fetch_panel_info(panel_id)
                    if panel_info:
                        self.panel_info = panel_info

                    self.panel_info_failed = False
                    self.write_startup_config()
                    self.display_panel_info()
                    time.sleep(1)
            except Exception as ex:
                self.panel_info_failed = True
                logging.exception(ex)

            time.sleep(1)


    def register(self):
        if PANEL_ID:
            return PANEL_ID
        else:
            panel_id = None
            while True:
                try:
                    log('Registering panel at: ' + REGISTRATION_URL)
                    panel_id = register(REGISTRATION_URL)
                    self.registration_failed = False
                except Exception as ex:
                    logging.exception(ex)
                    self.registration_failed = True

                if self.registration_failed:
                    if self.panel_info and not panel_id:
                        self.display_panel_info()
                    else:
                        self.display_init_screen()

                    time.sleep(1)
                else:
                    self.registration_failed = False
                    return panel_id

    def display_signage_itftournament(self):
        # XXX the panel must be started in VERTICAL mode (./m1_vertical.sh)

        # s.https://suprematic.slack.com/archives/DF1LE3XLY/p1719413956323839

        tournament_name = self.panel_info.get("tournament-name") or "Welcome!"
        self.draw_tournament_title(tournament_name)

        courts = self.panel_info.get("courts")
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
                if match.get("is-doubles"):
                    t1p1name = t1.get("player1").get("name")
                    t1p2name = t1.get("player2").get("name")
                    t2p1name = t2.get("player1").get("name")
                    t2p2name = t2.get("player2").get("name")
                    t1p1flag = t1.get("player1").get("flag")
                    t1p2flag = t1.get("player2").get("flag")
                    t2p1flag = t2.get("player1").get("flag")
                    t2p2flag = t2.get("player2").get("flag")
                    self.draw_signage_match_doubles([court_index, court_name],
                                        [[t1p1name, t1p1flag], [t1p2name, t1p2flag]],
                                        [[t2p1name, t2p1flag], [t2p2name, t2p2flag]],
                                        set_scores)
                else:

                    t1_name = t1.get("name").split(",")[0]  # FIXME remove it when data is properly set
                    t1_flag = t1.get("flag")
                    t2_name = t2.get("name").split(",")[0]  # FIXME remove it when data is properly set
                    t2_flag = t2.get("flag")
                    self.draw_signage_match_singles(court_index, court_name, t1_name, t2_name, t1_flag, t2_flag,
                                                    t1_set1, t2_set1, t1_set2, t2_set2, t1_set3, t2_set3)
            else:
                self.draw_signage_match_singles(court_index, court_name, "", "")
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

        self.draw_signage_tournament_sponsors()

    def draw_signage_court_name(self, x: int, y0: int, court_name):
        y = y0
        graphics.DrawLine(self.canvas, x, y, W_PANEL, y, COLOR_SIGNAGE_FG_COURT_SEPARATOR_LINE)
        y += 1
        fill_rect(self.canvas, x, y, 64, 1 + H_FONT_XXS + 1, COLOR_SIGNAGE_BG_COURT_NAME)
        y += H_FONT_XXS + 1
        graphics.DrawText(self.canvas, FONT_XXS, x + 1, y, COLOR_SIGNAGE_FG_COURT_NAME, court_name or '')
        y += 1
        graphics.DrawLine(self.canvas, x, y, W_PANEL, y, COLOR_SIGNAGE_FG_COURT_SEPARATOR_LINE)
        y += 1
        return y - y0  # 9

    def draw_signage_flag(self, flag_file, x, y):
        image = Image.open(flag_file).convert('RGB')
        image.thumbnail((W_FLAG_SMALL, H_FLAG_SMALL), Image.LANCZOS)
        self.canvas.SetImage(image, x, y)

    def draw_signage_match_team(self, x0: int, y0: int, team_name, team_flag,
                                score_set1, color_set1, score_set2, color_set2, score_set3, color_set3):
        y = y0
        if team_flag:
            w_flag = W_FLAG_SMALL
            x_name = x0 + W_FLAG_SMALL + 1
            team_flag_file = "images/flags/" + team_flag + ".png"
            self.draw_signage_flag(team_flag_file, x0, y)
        else:
            w_flag = 0
            x_name = x0

        y += H_FONT_XS
        w_name_max = W_TILE - w_flag
        if score_set3 is not None:
            w_name_max = X_SET1 - 2 - w_flag
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET1, y, color_set1, str(score_set1))
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET2, y, color_set2, str(score_set2))
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET3, y, color_set3, str(score_set3))
        elif score_set2 is not None:
            w_name_max = X_SET2 - 2 - w_flag
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET2, y, color_set1, str(score_set1))
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET3, y, color_set2, str(score_set2))
        elif score_set1 is not None:
            w_name_max = X_SET3 - 2 - w_flag
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET3, y, color_set1, str(score_set1))

        team_name_truncated = truncate_text(FONT_XS, w_name_max, team_name)
        graphics.DrawText(self.canvas, FONT_XS, x_name, y, COLOR_SIGNAGE_FG_TEAM_NAME, team_name_truncated)

    def draw_signage_match_team_flags(self, x0: int, y0: int, p1flag, p2flag,
                                      score_set1, color_set1, score_set2, color_set2, score_set3, color_set3):
        y = y0
        x = x0 + 7
        self.draw_signage_flag("images/flags/" + (p1flag or "VOID") + ".png", x, y)
        x += W_FLAG_SMALL + 12
        self.draw_signage_flag("images/flags/" + (p2flag or "VOID") + ".png", x, y)
        y += H_FONT_XS
        x = x0 + 7 + W_FLAG_SMALL + 4
        graphics.DrawText(self.canvas, FONT_XS, x, y, COLOR_SIGNAGE_FG_TEAM_NAME, "/")
        if score_set3 is not None:
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET1, y, color_set1, str(score_set1))
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET2, y, color_set2, str(score_set2))
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET3, y, color_set3, str(score_set3))
        elif score_set2 is not None:
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET2, y, color_set1, str(score_set1))
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET3, y, color_set2, str(score_set2))
        elif score_set1 is not None:
            graphics.DrawText(self.canvas, FONT_XS, x0 + X_SET3, y, color_set1, str(score_set1))

    def draw_signage_match_singles(self, court_index: int, court_name, t1_name, t2_name, t1_flag=None, t2_flag=None,
                                   t1_set1=None, t2_set1=None, t1_set2=None, t2_set2=None, t1_set3=None, t2_set3=None):

        color_set1 = color_set2 = color_set3 = [None, None]
        if t1_set3 is not None:
            color_set1 = score_color(t1_set1, t2_set1)
            color_set2 = score_color(t1_set2, t2_set2)
            color_set3 = score_color(t1_set3, t2_set3, False)
        elif t1_set2 is not None:
            color_set1 = score_color(t1_set1, t2_set1)
            color_set2 = score_color(t1_set2, t2_set2, False)
        elif t1_set1 is not None:
            color_set1 = score_color(t1_set1, t2_set1, False)

        y0 = 32 * court_index if ORIENTATION_VERTICAL else (0 if court_index % 2 else H_TILE)
        x0 = 0 if ORIENTATION_VERTICAL else (W_TILE if court_index < 3 else W_TILE * 2)

        h_court_name = self.draw_signage_court_name(x0, y0, court_name)

        y = y0 + h_court_name + 4

        self.draw_signage_match_team(x0, y, t1_name, t1_flag,
                                     t1_set1, color_set1[0],
                                     t1_set2, color_set2[0],
                                     t1_set3, color_set3[0])

        y += 9

        self.draw_signage_match_team(x0, y, t2_name, t2_flag,
                                     t2_set1, color_set1[1],
                                     t2_set2, color_set2[1],
                                     t2_set3, color_set3[1])

    def draw_signage_match_doubles(self, court, t1, t2, score):

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
            color_set1 = score_color(t1_set1, t2_set1)
            color_set2 = score_color(t1_set2, t2_set2)
            color_set3 = score_color(t1_set3, t2_set3, False)
        elif t1_set2 is not None:
            color_set1 = score_color(t1_set1, t2_set1)
            color_set2 = score_color(t1_set2, t2_set2, False)
        elif t1_set1 is not None:
            color_set1 = score_color(t1_set1, t2_set1, False)

        y0 = 32 * court_index if ORIENTATION_VERTICAL else (0 if court_index % 2 else H_TILE)
        x0 = 0 if ORIENTATION_VERTICAL else (W_TILE if court_index < 3 else W_TILE * 2)

        h_court_name = self.draw_signage_court_name(x0, y0, court_name)

        y = y0 + h_court_name + 4

        seconds_now = int(time.time())
        seconds_passed = seconds_now - SECONDS_START
        PERIOD_DOUBLES_FRAME_S = 4 # seconds

        if (seconds_passed // PERIOD_DOUBLES_FRAME_S) % 2:
            # draw names

            t1_name = t1p1name[:4] + "/" + t1p2name[:4]
            t2_name = t2p1name[:4] + "/" + t2p2name[:4]

            self.draw_signage_match_team(x0, y, t1_name, None,
                                         t1_set1, color_set1[0],
                                         t1_set2, color_set2[0],
                                         t1_set3, color_set3[0])

            y += 9

            self.draw_signage_match_team(x0, y, t2_name, None,
                                         t2_set1, color_set1[1],
                                         t2_set2, color_set2[1],
                                         t2_set3, color_set3[1])
        else:
            # draw flags
            self.draw_signage_match_team_flags(x0, y, t1p1flag, t1p2flag,
                                         t1_set1, color_set1[0],
                                         t1_set2, color_set2[0],
                                         t1_set3, color_set3[0])

            y += 9

            self.draw_signage_match_team_flags(x0, y, t2p1flag, t2p2flag,
                                               t1_set1, color_set1[0],
                                               t1_set2, color_set2[0],
                                               t1_set3, color_set3[0])

    def draw_tournament_title(self, title):
        fill_rect(self.canvas, 0, 0, W_TILE, H_TILE, COLOR_SIGNAGE_BG_TOURNAMENT_NAME)
        font = FONT_S
        lines = title.split(" ", 1)
        y = y_font_center(font, H_TILE / len(lines))
        for line in lines:
            x = x_font_center(line, W_TILE, font)
            graphics.DrawText(self.canvas, font, x, y, COLOR_SIGNAGE_FG_TOURNAMENT_NAME, line)
            y += font.height

    def draw_signage_tournament_sponsors(self):

        seconds_now = int(time.time())
        seconds_passed = seconds_now - SECONDS_START
        sponsor_index = (seconds_passed // PERIOD_SPONSOR_FRAME_S) % len(IMAGES_SPONSOR_LOGOS)

        file_image = IMAGES_SPONSOR_LOGOS[sponsor_index]
        x = 0
        y = H_PANEL - H_TILE
        self.canvas.SetImage(Image.open(file_image).convert('RGB'), x, y)

    def display_logo(self, image, show_clock):
        w = W_PANEL
        if ORIENTATION_HORIZONTAL and show_clock:
            w = W_LOGO_WITH_CLOCK

        x = (w - image.width) / 2
        y = (H_PANEL - image.height) / 2
        self.canvas.SetImage(image.convert('RGB'), x, y)

    def display_idle_mode_image_preset(self):
        idle_info = self.panel_info.get('idle-info')
        image_preset = idle_info.get('image-preset')
        path = "images/logos/" + image_preset
        image = Image.open(path)
        is_enough_space_for_clock = image.width < W_LOGO_WITH_CLOCK
        self.display_logo(image, is_enough_space_for_clock)
        if is_enough_space_for_clock and idle_info.get('clock') == True:
            self.display_clock_mode()

    def download_idle_mode_image(self, image_url):
        return Image.open(requests.get(image_url, stream=True).raw)

    def save_idle_mode_image(self, image):
        show_clock = image.width < W_LOGO_WITH_CLOCK
        image_max_width = W_LOGO_WITH_CLOCK if show_clock else W_PANEL
        image = thumbnail(image, image_max_width)
        image.save(LATEST_IDLE_MODE_IMAGE_PATH, 'png')
        return (image, show_clock)

    def display_ebusy_ads(self):
        ebusy_ads = self.panel_info.get('ebusy-ads')
        id = ebusy_ads.get("id")
        url = ebusy_ads.get("url")
        path = IMAGE_CACHE_DIR + "/ebusy_" + str(id)

        try:
            if (os.path.isfile(path)):
                image = Image.open(path)
            else:
                image = self.download_idle_mode_image(url)
                image.save(path, 'png')

            x = (W_PANEL - image.width) / 2
            y = (H_PANEL - image.height) / 2
            self.canvas.SetImage(image.convert('RGB'), x, y)

        except Exception as e:
            logging.exception(e)
            log('Error downloading image', e)

    def display_idle_mode_image_url(self):
        idle_info = self.panel_info.get('idle-info')
        image_url = idle_info.get('image-url')
        image_url = BASE_URL + "/" + image_url

        try:
            request = urllib.request.Request(image_url, method="HEAD")
            response = urllib.request.urlopen(request)
            etag = str(response.headers["ETag"])

            if etag != None:
                path = IMAGE_CACHE_DIR + "/" + etag
                if (os.path.isfile(path)):
                    image = Image.open(path)
                    show_clock = self.save_idle_mode_image(image)[1]
                else:
                    saved = self.save_idle_mode_image(self.download_idle_mode_image(image_url))
                    image = saved[0]
                    show_clock = saved[1]
                    image.save(path, 'png')
            else:
                saved = self.save_idle_mode_image(self.download_idle_mode_image(image_url))
                image = saved[0]
                show_clock = saved[1]

            self.display_logo(image, show_clock)
            if show_clock and idle_info.get('clock') == True:
                self.display_clock_mode()
        except Exception as e:
            logging.exception(e)
            log('Error downloading image', e)

    def display_idle_mode_message(self):
        idle_info = self.panel_info.get('idle-info')

        message = idle_info.get('message', '')
        h_available = H_PANEL - 2 - 20 - 2 # minus clock
        w_available = W_PANEL

        lines = message.split('\n')

        if len(lines) == 1:
            l0 = lines[0]
            font = pick_font_that_fits(w_available, h_available, l0)
            x0 = max(0, (w_available - width_in_pixels(font, l0)) / 2)
            y0 = y_font_center(font, h_available)
            graphics.DrawText(self.canvas, font, x0, y0, COLOR_BOOKING_GREETING, l0)
        else:
            l0 = lines[0]
            l1 = lines[1]
            font = pick_font_that_fits(w_available, h_available, l0, l1)

            x0 = max(0, (w_available - width_in_pixels(font, l0)) / 2)
            y0 = y_font_center(font, h_available / 2)
            graphics.DrawText(self.canvas, font, x0, y0, COLOR_BOOKING_GREETING, l0)

            x1 = max(0, (w_available - width_in_pixels(font, l1)) / 2)
            y1 = y0 + y_font_center(font, h_available / 2)
            graphics.DrawText(self.canvas, font, x1, y1, COLOR_BOOKING_GREETING, l1)

        if idle_info.get('clock') == True:
            self.display_clock_mode()

    def display_panel_info(self):
        self.canvas.Clear()

        if self.registration_failed or self.panel_info_failed:
            self.draw_error_indicator(self.panel_info.get('standby'))

        if self.panel_info.get('standby'):
            idle_info = self.panel_info.get('idle-info', {})
            if not idle_info.get('image-preset') and \
                not idle_info.get('image-url') and \
                not idle_info.get('message'):
                self.display_clock_mode()
        elif 'booking' in self.panel_info:
            self.display_booking()
        elif 'ebusy-ads' in self.panel_info:
            self.display_ebusy_ads()
        elif 'idle-info' in self.panel_info:
            self.display_idle_mode()
        elif 'tournament-name' in self.panel_info:
            self.display_signage_itftournament()
        elif 'team1' in self.panel_info:
            self.display_match()

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def display_idle_mode(self):
        idle_info = self.panel_info.get('idle-info')
        if idle_info.get('image-preset'):
            self.display_idle_mode_image_preset()
        elif idle_info.get('image-url'):
            self.display_idle_mode_image_url()
        elif idle_info.get('message'):
            self.display_idle_mode_message()
        elif idle_info.get('clock'):
            self.display_clock_mode()

    def display_init_screen(self):
        self.canvas.Clear()
        dt = datetime.now()
        text = dt.strftime('%H:%M')
        x = W_LOGO_WITH_CLOCK + 2 if ORIENTATION_HORIZONTAL else (x_font_center(text, W_PANEL, FONT_CLOCK))
        y = 62 if ORIENTATION_HORIZONTAL else H_PANEL - 2
        draw_text(self.canvas, x, y, text, FONT_CLOCK, COLOR_CLOCK)
        self.draw_error_indicator()
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def display_clock_mode(self):

        panel_tz = self.panel_tz()
        dt = datetime.now(tz.gettz(panel_tz))
        text = dt.strftime('%H:%M')
        color = COLOR_CLOCK_STANDBY if self.panel_info.get('standby') else COLOR_CLOCK

        clock = self.panel_info.get('idle-info', {}).get('clock')
        if clock == True: # Compiler warning is WRONG!
            # display a clock along with some other elements, using the default Spleen font
            font = FONT_CLOCK_S_2
            if ORIENTATION_VERTICAL:
                x = x_font_center(text, W_PANEL, FONT_CLOCK)
                y = H_PANEL - 2
            else:
                x = W_LOGO_WITH_CLOCK # - 2
                y = 62
        elif clock:
            if ORIENTATION_VERTICAL:
                font = FONT_CLOCK_S_2
                x = x_font_center(text, W_PANEL, FONT_CLOCK)
                y = H_PANEL - 2
            else:
                clock_size = clock.get('size')
                clock_font = clock.get('font')
                clock_h_align = clock.get('h-align')
                clock_v_align = clock.get('v-align')

                if clock_font == "font-2":
                    if clock_size == "small":
                        font = FONT_CLOCK_S_2
                    elif clock_size == "medium":
                        font = FONT_CLOCK_M_2
                    else:
                        font = FONT_CLOCK_L_2
                else:
                    if clock_size == "small":
                        font = FONT_CLOCK_S_1
                    elif clock_size == "medium":
                        font = FONT_CLOCK_M_1
                    else:
                        font = FONT_CLOCK_L_1

                if clock_h_align == "left":
                    x = 0
                elif clock_h_align == "center":
                    x = (W_PANEL - width_in_pixels(font, text)) / 2
                else:
                    x = W_LOGO_WITH_CLOCK - 1

                if clock_v_align == "top":
                    y = y_font_offset(font)
                elif clock_v_align == "center":
                    y = (H_PANEL + y_font_offset(font))/2
                else:
                    y = H_PANEL
        else:
            return
        draw_text(self.canvas, x, y, text, font, color)

    def display_set_digit(self, x, y, font, color, score):
        # FIXME meh
        if score != "":
            if int(score) < 10:
                graphics.DrawText(self.canvas, font, x, y, color, str(score))
            else:
                score = str(int(score) % 10)
                fill_rect(self.canvas, x - 2, y + 1, width_in_pixels(font, score) + 2, -y_font_offset(font) - 3, color)
                graphics.DrawText(self.canvas, font, x, y, COLOR_BLACK, score)

    def display_score(self, match):
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
        fill_rect(self.canvas, x_score, 0, W_PANEL - x_score, H_PANEL, COLOR_SCORE_BACKGROUND)

        x_t1_score_game = X_SCORE_GAME if len(t1_game) != 1 else X_SCORE_GAME + 8
        x_t2_score_game = X_SCORE_GAME if len(t2_game) != 1 else X_SCORE_GAME + 8

        # Americano
        if not match.get("isTotalPointsMatch", False):
            self.display_set_digit(x_set1, y_t1, FONT_SCORE, c_t1_set1, t1_set1)
            self.display_set_digit(x_set2, y_t1, FONT_SCORE, c_t1_set2, t1_set2)
            self.display_set_digit(x_set3, y_t1, FONT_SCORE, c_t1_set3, t1_set3)

            self.display_set_digit(x_set1, y_t2, FONT_SCORE, c_t2_set1, t2_set1)
            self.display_set_digit(x_set2, y_t2, FONT_SCORE, c_t2_set2, t2_set2)
            self.display_set_digit(x_set3, y_t2, FONT_SCORE, c_t2_set3, t2_set3)

        graphics.DrawText(self.canvas, FONT_SCORE, x_t1_score_game, y_t1, COLOR_SCORE_GAME, t1_game)
        graphics.DrawText(self.canvas, FONT_SCORE, x_t2_score_game, y_t2, COLOR_SCORE_GAME, t2_game)

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
                draw_matrix(self.canvas, ball, X_SCORE_SERVICE, y_service_t1)
            elif t2_on_serve:
                draw_matrix(self.canvas, ball, X_SCORE_SERVICE, y_service_t2)

    def display_names(self, match):

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
                t1p1 = player_name(match["team1"]["p1"], "Player1")
                t2p1 = player_name(match["team2"]["p1"], "Player2")
            t1p2 = t2p2 = ''
        elif match["isDoubles"]:
            t1p1 = player_name(match["team1"]["p1"], "Player1")
            t1p2 = player_name(match["team1"]["p2"], "Player2")
            t2p1 = player_name(match["team2"]["p1"], "Player3")
            t2p2 = player_name(match["team2"]["p2"], "Player4")

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
            graphics.DrawText(self.canvas, font, x, y_t1, COLOR_TEAM_NAME, t1p1)
            graphics.DrawText(self.canvas, font, x, y_t2, COLOR_TEAM_NAME, t2p1)
            if display_flags:
                self.display_singles_flags(t1p1_flag, t2p1_flag)

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
            graphics.DrawText(self.canvas, font, x, y_t1p1, COLOR_TEAM_NAME, t1p1)
            graphics.DrawText(self.canvas, font, x, y_t1p2, COLOR_TEAM_NAME, t1p2)
            graphics.DrawText(self.canvas, font, x, y_t2p1, COLOR_TEAM_NAME, t2p1)
            graphics.DrawText(self.canvas, font, x, y_t2p2, COLOR_TEAM_NAME, t2p2)
            if display_flags:
                if same_flags_in_teams:
                    self.display_singles_flags(t1p1_flag, t2p1_flag)
                else:
                    # 2 (12) 3 (12) 3 3 (12) 3 (12) 2
                    y_flag_t1p1 = 2
                    y_flag_t1p2 = y_flag_t1p1 + H_FLAG + 3
                    y_flag_t2p1 = y_flag_t1p2 + H_FLAG + 3 + 3
                    y_flag_t2p2 = y_flag_t2p1 + H_FLAG + 3

                    if t1p1_flag is not None:
                        self.canvas.SetImage(t1p1_flag, 0, y_flag_t1p1)

                    if t1p2_flag is not None:
                        self.canvas.SetImage(t1p2_flag, 0, y_flag_t1p2)

                    if t2p1_flag is not None:
                        self.canvas.SetImage(t2p1_flag, 0, y_flag_t2p1)

                    if t2p2_flag is not None:
                        self.canvas.SetImage(t2p2_flag, 0, y_flag_t2p2)

    def display_singles_flags(self, img_t1, img_t2):
        if img_t1 is not None:
            y_flag_t1 = max(0, H_PANEL / 2 / 2 - img_t1.height / 2)
            self.canvas.SetImage(img_t1, 0, y_flag_t1)

        if img_t2 is not None:
            y_flag_t2 = max(H_PANEL / 2, H_PANEL / 2 + H_PANEL / 2 / 2 - img_t2.height / 2)
            self.canvas.SetImage(img_t2, 0, y_flag_t2)

    def display_winner(self, match):
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
            draw_matrix(self.canvas, cup, x_medal, medal_delta)
        elif match_result == "T2_WON":
            draw_matrix(self.canvas, cup, x_medal, H_PANEL / 2 + medal_delta)

    def display_match(self):
        self.display_names(self.panel_info)
        self.display_score(self.panel_info)
        self.display_winner(self.panel_info)

    def draw_error_indicator(self, standby=False):
        x = (COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)
        o = (
            COLOR_7C_BLUE_STANDBY.red if standby else COLOR_7C_BLUE.red,
            COLOR_7C_BLUE_STANDBY.green if standby else COLOR_7C_BLUE.green,
            COLOR_7C_BLUE_STANDBY.blue if standby else COLOR_7C_BLUE.blue
        )
        dot = [
            [x, o, o, x],
            [o, o, o, o],
            [o, o, o, o],
            [x, o, o, x]]
        draw_matrix(self.canvas, dot, W_PANEL - 4, H_PANEL - 4)

    def panel_tz(self):
        return self.panel_info.get('idle-info', {}).get('timezone', 'Europe/Berlin')

    def display_booking(self):
        overlap_minutes_td = timedelta(minutes=BOOKIN_OVERLAP_MINUTES)
        booking = self.panel_info.get('booking')
        court = booking.get('court')
        cur_booking = booking.get('current')
        next_booking = booking.get('next')
        panel_tz = self.panel_tz()

        # Use datetime set in admin panel UI for easier testing/debugging.
        _dev_timestamp = booking.get('_dev_timestamp')
        if _dev_timestamp and len(_dev_timestamp):
            t_now = parser.parse(_dev_timestamp)
        else:
            t_now = datetime.now(tz.gettz(panel_tz))

        if cur_booking:
            t_end_right = parser.parse(cur_booking['end-date'])
            t_end_left = t_end_right - overlap_minutes_td

            if t_now >= t_end_left:
                minutes_left = (t_end_right - t_now).seconds // 60 % 60
                if next_booking:
                    #  0 - 14 upcoming
                    # 15 - 29 timeleft
                    # 30 - 44 upcoming
                    # 45 - 59 timeleft
                    if (t_now.second >= 15 and t_now.second <= 29) or (t_now.second >= 45 and t_now.second <= 59):
                        self.display_booking_timeleft_match(cur_booking, court, t_now, minutes_left)
                    else:
                        self.display_booking_upcoming_match(next_booking, court, t_now)
                else:
                    self.display_booking_timeleft_match(cur_booking, court, t_now, minutes_left)
            else:
                self.display_booking_greeting(cur_booking, court, t_now)
        elif next_booking and t_now >= (parser.parse(next_booking['start-date']) - overlap_minutes_td):
            self.display_booking_upcoming_match(next_booking, court, t_now)

    def display_booking_header(self, court, dt):
        def display_text(x, y, text):
            draw_text(self.canvas, x, y, text, FONT_BOOKING, COLOR_BOOKING_GREETING)

        display_text(2, 10, court['name'])

        clock_str = dt.strftime('%H:%M')
        display_text(160, 10, clock_str)

    def display_booking_greeting(self, booking, court, dt):
        def display_text(x, y, text):
            draw_text(self.canvas, x, y, text, FONT_BOOKING, COLOR_BOOKING_GREETING)

        self.display_booking_header(court, dt)
        players = [p for p in [booking.get(k) for k in ['p1', 'p2', 'p3', 'p4']] if p]
        player_firstnames = [ p.get('firstname') for p in players]
        display_text(2, 25, 'Willkommen im MatchCenter')
        display_text(2, 40, ','.join(player_firstnames))

    def display_booking_timeleft_match(self, booking, court, dt, minutes_left):
        minutes_left_txt = '< 1' if minutes_left == 0 else str(minutes_left)
        self.display_booking_match(booking, court, dt, 'Noch: ' + minutes_left_txt + ' min.')

    def display_booking_upcoming_match(self, booking, court, dt):
        self.display_booking_match(booking, court, dt, 'Nachste')

    def display_booking_match(self, booking, court, dt, notification=''):
        def booking_team(isTeam1=True):
            def booking_player(player):
                txt = None
                firstname = player.get('firstname')
                if firstname:
                    txt = firstname
                lastname = player.get('lastname')
                if lastname:
                    if txt:
                        txt += ' '
                    txt += lastname
                return txt

            txt = None
            tp1 =  booking['p1'] if isTeam1 else booking.get('p3')
            if tp1:
                txt = booking_player(tp1)
            tp2 =  booking['p2'] if isTeam1 else booking.get('p4')
            if tp2:
                if txt:
                    txt += ' und '
                txt = (txt or '') + booking_player(tp2)
            return txt

        def display_text(x, y, text):
            draw_text(self.canvas, x, y, text, FONT_BOOKING, COLOR_BOOKING_GREETING)

        self.display_booking_header(court, dt)
        start_time = parser.parse(booking['start-date']).strftime('%H:%M')
        end_time = parser.parse(booking['end-date']).strftime('%H:%M')
        display_text(2, 25, start_time + ' - ' + end_time)

        t1 = booking_team()
        display_text(2, 40, t1)
        t2 = booking_team(False)
        if t2:
            display_text(2, 55, t2)

        if notification:
            display_text(105, 25, notification)

# Main function
if __name__ == "__main__":
    infoboard = SevenCourtsM1()
    if not infoboard.process():
        infoboard.print_help()
