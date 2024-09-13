#!/usr/bin/env python3

import os
# Set the environment variable USE_RGB_MATRIX_EMULATOR to use with emulator https://github.com/ty-porter/RGBMatrixEmulator
# Do not set to use with real SDK https://github.com/hzeller/rpi-rgb-led-matrix
if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
  from RGBMatrixEmulator import graphics
else:
  from rgbmatrix import graphics

from samplebase import SampleBase
from sevencourts import *
import time
import urllib.request
from urllib.error import URLError, HTTPError
from datetime import datetime
from PIL import Image
import json
import socket
import logging
import requests
import subprocess

GIT_COMMIT_ID = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()

# FIXME use not hardcoded directory (TBD)
IMAGE_CACHE_DIR = "/opt/7c/cache-images"
os.makedirs(IMAGE_CACHE_DIR, exist_ok = True)
# The default 0o777 does not work, see https://stackoverflow.com/questions/5231901/permission-problems-when-creating-a-dir-with-os-makedirs-in-python
os.chmod(IMAGE_CACHE_DIR, 0o777)

LATEST_IDLE_MODE_IMAGE_PATH = IMAGE_CACHE_DIR + '/latest_idle_image'

PANEL_NAME = socket.gethostname()

BASE_URL = os.getenv('TABLEAU_SERVER_BASE_URL', 'https://prod.tableau.tennismath.com')

REGISTRATION_URL = BASE_URL + "/panels/"

PANEL_ID = os.getenv('TABLEAU_PANEL_ID')

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
  FONT_CLOCK = FONT_L
  FONT_SCORE = FONT_L
else:
  FONT_CLOCK = FONTS_V0[0]
  FONT_SCORE = FONTS_V0[0]

COLOR_CLOCK = COLOR_GREY
COLOR_CLOCK_STANDBY = COLOR_GREY_DARKEST

UPPER_CASE_NAMES = True
MARGIN_NAMES_SCOREBOARD = 3

X_MIN_SCOREBOARD = int(PANEL_WIDTH / 2)
W_SCORE_SET = 20
X_SCORE_GAME = 163
X_SCORE_SERVICE = 155

W_LOGO_WITH_CLOCK = 122 # left from clock

def panel_info_url(panel_id):
    return BASE_URL + "/panels/" + panel_id + "/match"

def uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            return float(f.readline().split()[0])
    except Exception as e:
        log(e, 'Cannot get uptime')
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
    except Exception as e:
        log(e, 'Cannot get CPU temperature')
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
            return match or None # FIX: the server can return False if match is over, this leads to error then
        elif response.status == 205:
            idle_info = json.loads(response.read().decode('utf-8') or 'null')
            log("idle-info:", idle_info)
            return idle_info
    return None

def player_name(p, noname="Noname"):
    return p["lastname"] or p["firstname"] or noname

def thumbnail(image, w=PANEL_WIDTH, h=PANEL_HEIGHT):
    # print ("original w: {0}, h: {1}".format(image.width, image.height))
    if (image.width > w or image.height > h):
        image.thumbnail((w, h), Image.LANCZOS)
    # print ("result w: {0}, h: {1}".format(image.width, image.height))
    return image

class SevenCourtsM1(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SevenCourtsM1, self).__init__(*args, **kwargs)
        self.last_known_club_mode = None
        self.last_known_club_mode_arg = None
        self.is_standby = False

    def run(self):
        self.canvas = self.matrix.CreateFrameCanvas()
        self.display_idle_mode(None)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

        while True:
            panel_id = self.register()
            match = None

            try:
                while True:
                    self.canvas.Clear()
                    panel_info = fetch_panel_info(panel_id)

                    if panel_info is not None:
                        self.is_standby = panel_info.get("standby", False)

                    if self.is_standby or panel_info == None:
                        self.display_idle_mode(None)
                    elif 'ebusy' in panel_info:
                        ebusy = panel_info.get("ebusy")
                        if 'greeting' in ebusy:
                            self.display_ebusy_greeting(ebusy)
                    elif 'idle-info' in panel_info:
                        self.display_idle_mode(panel_info["idle-info"])
                    elif 'team1' in panel_info:
                        self.display_match(panel_info)
                    self.canvas = self.matrix.SwapOnVSync(self.canvas)
                    time.sleep(1)
            except URLError as e:
                logging.exception(e)
                log('URLError in #run', e)
            except socket.timeout as e:
                logging.exception(e)
                log('Socket timeout in #run', e)
            except Exception as e:
                logging.exception(e)
                log('Unexpected exception in #run', e)

    def register(self):
        if PANEL_ID:
            return PANEL_ID
        else:
            panel_id = None
            while True:
                self.canvas.Clear()

                url = REGISTRATION_URL;
                try:
                    log('Registering panel at: ' + url)
                    panel_id = register(url)
                except URLError as e:
                    log(e.reason, url, '#register')
                    self.display_last_known_club_mode()
                    self.draw_error_indicator()
                except socket.timeout as e:
                    logging.exception(e)
                    log('Socket timeout in #register', e)
                    self.display_last_known_club_mode()
                    self.draw_error_indicator()
                except Exception as e:
                    logging.exception(e)
                    log('Unexpected exception in #register', e)
                    self.display_last_known_club_mode()
                    self.draw_error_indicator()

                if panel_id != None:
                    return panel_id
                else:
                    self.display_idle_mode(None)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                time.sleep(1)

    def display_logo(self, image, show_clock):
        w = W_LOGO_WITH_CLOCK if show_clock else PANEL_WIDTH
        x = (w - image.width) / 2
        y = (PANEL_HEIGHT - image.height) / 2
        self.canvas.SetImage(image.convert('RGB'), x, y)

    def display_idle_mode_image_preset(self, image_preset):
        self.last_known_club_mode = 'image-preset'
        self.last_known_club_mode_arg = image_preset

        path = "images/logos/" + image_preset
        image = Image.open(path)
        show_clock = image.width < W_LOGO_WITH_CLOCK
        self.display_logo(image, show_clock)
        return show_clock

    def download_idle_mode_image(self, image_url):
        return Image.open(requests.get(image_url, stream=True).raw)

    def save_idle_mode_image(self, image):
        show_clock = image.width < W_LOGO_WITH_CLOCK
        image_max_width = W_LOGO_WITH_CLOCK if show_clock else PANEL_WIDTH
        image = thumbnail(image, image_max_width)
        image.save(LATEST_IDLE_MODE_IMAGE_PATH, 'png')
        return (image, show_clock)

    def display_idle_mode_image_url(self, p_image_url):
        self.last_known_club_mode = 'image-url'
        self.last_known_club_mode_arg = p_image_url

        image_url = BASE_URL + "/" + p_image_url
        show_clock = True

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
        except Exception as e:
            logging.exception(e)
            log('Error downloading image', e)
        return show_clock

    def display_idle_mode_message(self, p_message):
        self.last_known_club_mode = 'message'
        self.last_known_club_mode_arg = p_message

        message = p_message or ''
        color = COLOR_BLUE_7c
        h_available = PANEL_HEIGHT - 2 - 20 - 2 # minus clock
        w_available = PANEL_WIDTH

        lines = message.split('\n')

        if len(lines) == 1:
            l0 = lines[0]
            font = pick_font_that_fits(w_available, h_available, l0)
            x0 = max(0, (w_available - width_in_pixels(font, l0)) / 2)
            y0 = y_font_center(font, h_available)
            graphics.DrawText(self.canvas, font, x0, y0, color, l0)
        else:
            l0 = lines[0]
            l1 = lines[1]
            font = pick_font_that_fits(w_available, h_available, l0, l1)

            x0 = max(0, (w_available - width_in_pixels(font, l0)) / 2)
            y0 = y_font_center(font, h_available / 2)
            graphics.DrawText(self.canvas, font, x0, y0, color, l0)

            x1 = max(0, (w_available - width_in_pixels(font, l1)) / 2)
            y1 = y0 + y_font_center(font, h_available / 2)
            graphics.DrawText(self.canvas, font, x1, y1, color, l1)

        return True

    def display_last_known_club_mode(self):
        if self.last_known_club_mode == 'image-preset':
            self.display_idle_mode_image_preset(self.last_known_club_mode_arg)
        elif self.last_known_club_mode == 'image-url':
            if (os.path.isfile(LATEST_IDLE_MODE_IMAGE_PATH)):
                image = Image.open(LATEST_IDLE_MODE_IMAGE_PATH)
                show_clock = image.width < W_LOGO_WITH_CLOCK
                self.display_logo(image, show_clock)
                if show_clock:
                    self.display_clock()
        elif self.last_known_club_mode == 'message':
            self.display_idle_mode_message(self.last_known_club_mode_arg)
        elif self.last_known_club_mode == None:
            self.display_idle_mode(None)

    def display_idle_mode(self, idle_info):
        if self.is_standby:
            self.display_clock()
        elif idle_info != None:
            show_clock = True

            if 'image-preset' in idle_info and idle_info["image-preset"] != None:
                show_clock = self.display_idle_mode_image_preset(idle_info["image-preset"])
            elif 'image-url' in idle_info and idle_info["image-url"] != None:
                show_clock = self.display_idle_mode_image_url(idle_info["image-url"])
            else:
                show_clock = self.display_idle_mode_message(idle_info["message"])

            if show_clock:
                self.display_clock()
        else:
            # TODO display something neutral instead of clock
            if self.last_known_club_mode == None:
                self.display_clock()

    def display_clock(self):
        text = datetime.now().strftime('%H:%M')
        color = COLOR_CLOCK_STANDBY if self.is_standby else COLOR_CLOCK
        draw_text(self.canvas, W_LOGO_WITH_CLOCK + 2, 62, text, FONT_CLOCK, color)

    def display_set_digit(self, x, y, font, color, score):
        # FIXME meh
        if (score != ""):
            if int(score) < 10:
                graphics.DrawText(self.canvas, font, x, y, color, str(score))
            else:
                score = str(int(score) % 10)
                fill_rect(self.canvas, x-2, y+1, width_in_pixels(font, score)+2, -y_font_offset(font)-3, color)
                graphics.DrawText(self.canvas, font, x, y, COLOR_BLACK, score)

    def display_score(self, match):
        t1_on_serve=match["team1"]["serves"]
        t2_on_serve=match["team2"]["serves"]
        t1_set_scores = match["team1"]["setScores"] or []
        t2_set_scores = match["team2"]["setScores"] or []

        is_match_over = match["matchResult"] in ('T1_WON', 'T2_WON', 'DRAW')

        t1_game = match["team1"].get("gameScore", "")
        t2_game = match["team2"].get("gameScore", "")
        t1_game = str(t1_game if t1_game != None else "")
        t2_game = str(t2_game if t2_game != None else "")

        if (len(t1_set_scores)==0):
            t1_set1 = t2_set1 = t1_set2 = t2_set2 = t1_set3 = t2_set3 = ""
            c_t1_set1 = c_t2_set1 = c_t1_set2 = c_t2_set2 = c_t1_set3 = c_t2_set3 = COLOR_BLACK
            x_set1 = x_set2 = x_set3 = PANEL_WIDTH
        elif (len(t1_set_scores)==1):
            t1_set1 = match["team1"]["setScores"][0]
            t2_set1 = match["team2"]["setScores"][0]
            t1_set2 = t2_set2 = t1_set3 = t2_set3 = ""

            if is_match_over:
                c_t1_set1 = COLOR_SCORE_SET_WON if t1_set1>t2_set1 else COLOR_SCORE_SET_LOST
                c_t2_set1 = COLOR_SCORE_SET_WON if t2_set1>t1_set1 else COLOR_SCORE_SET_LOST
            else:
                c_t1_set1 = c_t2_set1 = COLOR_SCORE_SET
            c_t1_set2 = c_t2_set2 = c_t1_set3 = c_t2_set3 = COLOR_BLACK
            x_set1 = X_MIN_SCOREBOARD + W_SCORE_SET + W_SCORE_SET
            x_set2 = x_set3 = PANEL_WIDTH

        elif (len(t1_set_scores)==2):
            t1_set1 = match["team1"]["setScores"][0]
            t2_set1 = match["team2"]["setScores"][0]
            t1_set2 = match["team1"]["setScores"][1]
            t2_set2 = match["team2"]["setScores"][1]
            t1_set3 = t2_set3 = ""

            c_t1_set1 = COLOR_SCORE_SET_WON if t1_set1>t2_set1 else COLOR_SCORE_SET_LOST
            c_t2_set1 = COLOR_SCORE_SET_WON if t2_set1>t1_set1 else COLOR_SCORE_SET_LOST
            if is_match_over:
                c_t1_set2 = COLOR_SCORE_SET_WON if t1_set2>t2_set2 else COLOR_SCORE_SET_LOST
                c_t2_set2 = COLOR_SCORE_SET_WON if t2_set2>t1_set2 else COLOR_SCORE_SET_LOST
            else:
                c_t1_set2 = c_t2_set2 = COLOR_SCORE_SET
            c_t1_set3 = c_t2_set3 = COLOR_BLACK
            x_set1 = X_MIN_SCOREBOARD + W_SCORE_SET
            x_set2 = x_set1 + W_SCORE_SET
            x_set3 = PANEL_WIDTH

        else: # (len(t1_set_scores)==3) -- 4+ sets are not supported yet
            t1_set1 = match["team1"]["setScores"][0]
            t2_set1 = match["team2"]["setScores"][0]
            t1_set2 = match["team1"]["setScores"][1]
            t2_set2 = match["team2"]["setScores"][1]
            t1_set3 = match["team1"]["setScores"][2]
            t2_set3 = match["team2"]["setScores"][2]
            c_t1_set1 = COLOR_SCORE_SET_WON if t1_set1>t2_set1 else COLOR_SCORE_SET_LOST
            c_t2_set1 = COLOR_SCORE_SET_WON if t2_set1>t1_set1 else COLOR_SCORE_SET_LOST
            c_t1_set2 = COLOR_SCORE_SET_WON if t1_set2>t2_set2 else COLOR_SCORE_SET_LOST
            c_t2_set2 = COLOR_SCORE_SET_WON if t2_set2>t1_set2 else COLOR_SCORE_SET_LOST
            if is_match_over:
                c_t1_set3 = COLOR_SCORE_SET_WON if t1_set3>t2_set3 else COLOR_SCORE_SET_LOST
                c_t2_set3 = COLOR_SCORE_SET_WON if t2_set3>t1_set3 else COLOR_SCORE_SET_LOST

                # A crutch fix to nicely display match-tie-break result.
                # FIXME Match/score metadata is missing to do it properly.
                is_match_tiebreak = t1_set3>=10 or t2_set3>=10
                if is_match_tiebreak:
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

                GAME_SCORES = ('15', '30', '40', 'A')
                # meh, this will not work when score in MTB will be 15 what is rare but not excluded
                # FIXME Match/score metadata is missing to do it properly.
                is_match_tiebreak = t1_set3==0 and t2_set3==0 and t1_game not in GAME_SCORES and t2_game not in GAME_SCORES
                if is_match_tiebreak:
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
        y_T1 = y_font_center(FONT_SCORE, PANEL_HEIGHT/2)
        y_T2 = y_T1 + (PANEL_HEIGHT/2)

        # "cover" the score area so that names do not intersect
        x_score = min(x_set1, X_SCORE_SERVICE) - MARGIN_NAMES_SCOREBOARD
        fill_rect(self.canvas, x_score, 0, PANEL_WIDTH - x_score, PANEL_HEIGHT, COLOR_SCORE_BACKGROUND)

        x_T1_score_game = X_SCORE_GAME if len(t1_game) != 1 else X_SCORE_GAME + 8
        x_T2_score_game = X_SCORE_GAME if len(t2_game) != 1 else X_SCORE_GAME + 8

        # Americano
        if match.get("isTotalPointsMatch", False) != True:
            self.display_set_digit(x_set1, y_T1, FONT_SCORE, c_t1_set1, t1_set1)
            self.display_set_digit(x_set2, y_T1, FONT_SCORE, c_t1_set2, t1_set2)
            self.display_set_digit(x_set3, y_T1, FONT_SCORE, c_t1_set3, t1_set3)

            self.display_set_digit(x_set1, y_T2, FONT_SCORE, c_t2_set1, t2_set1)
            self.display_set_digit(x_set2, y_T2, FONT_SCORE, c_t2_set2, t2_set2)
            self.display_set_digit(x_set3, y_T2, FONT_SCORE, c_t2_set3, t2_set3)

        graphics.DrawText(self.canvas, FONT_SCORE, x_T1_score_game, y_T1, COLOR_SCORE_GAME, t1_game)
        graphics.DrawText(self.canvas, FONT_SCORE, x_T2_score_game, y_T2, COLOR_SCORE_GAME, t2_game)

        # service indicator
        if match.get("hideServiceIndicator", False) != True and not is_match_over:
            b = (0, 0 ,0)
            y = (255, 255, 0)
            ball = [
                [b,b,y,y,y,b,b],
                [b,y,y,y,y,y,b],
                [y,y,y,y,y,y,y],
                [y,y,y,y,y,y,y],
                [y,y,y,y,y,y,y],
                [b,y,y,y,y,y,b],
                [b,b,y,y,y,b,b]]
            y_service_t1 = int(PANEL_HEIGHT/2/2 - len(ball)/2)
            y_service_t2 = y_service_t1 + PANEL_HEIGHT/2
            if t1_on_serve:
                draw_matrix(self.canvas, ball, X_SCORE_SERVICE, y_service_t1)
            elif t2_on_serve:
                draw_matrix(self.canvas, ball, X_SCORE_SERVICE, y_service_t2)



    def display_names(self, match):

        ios_teca_client_v1_1_27 = match["team1"]["p1"] == None and match["team2"]["p1"] == None

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

        t1p1_flag_len = 0 if t1p1_flag == None else len(t1p1_flag)
        t1p2_flag_len = 0 if t1p2_flag == None else len(t1p2_flag)
        t2p1_flag_len = 0 if t2p1_flag == None else len(t2p1_flag)
        t2p2_flag_len = 0 if t2p2_flag == None else len(t2p2_flag)

        display_flags = max(t1p1_flag_len, t1p2_flag_len, t2p1_flag_len, t2p2_flag_len) > 0
        same_flags_in_teams = (t1p1_flag == t1p2_flag) & (t2p1_flag == t2p2_flag)
        if display_flags:
            t1p1_flag = None if not t1p1_flag else load_flag_image(t1p1_flag)
            t1p2_flag = None if not t1p2_flag else load_flag_image(t1p2_flag)
            t2p1_flag = None if not t2p1_flag else load_flag_image(t2p1_flag)
            t2p2_flag = None if not t2p2_flag else load_flag_image(t2p2_flag)
            flag_width = FLAG_WIDTH
        else:
            flag_width = 0

        # 2. names
        t1_set_scores = match["team1"]["setScores"] or []
        t2_set_scores = match["team2"]["setScores"] or []
        if (len(t1_set_scores)==0):
            x_scoreboard = X_SCORE_SERVICE
        elif (len(t1_set_scores)==1):
            x_scoreboard = X_MIN_SCOREBOARD + W_SCORE_SET + W_SCORE_SET
        elif (len(t1_set_scores)==2):
            x_scoreboard = X_MIN_SCOREBOARD + W_SCORE_SET
        else: # (len(t1_set_scores)==3) -- 4+ sets are not supported yet
            x_scoreboard = X_MIN_SCOREBOARD
        name_max_width = x_scoreboard - flag_width - 1 - MARGIN_NAMES_SCOREBOARD

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
            name_max_height = int(PANEL_HEIGHT/2 - 2) #=>30
            font = pick_font_that_fits(name_max_width, name_max_height, t1p1, t2p1)
            y_t1 = y_font_center(font, PANEL_HEIGHT/2)
            y_t2 = y_t1 + PANEL_HEIGHT/2
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

            name_max_height = 1 + FLAG_HEIGHT + 1 #=> 14

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
                    y_flag_t1p2 = y_flag_t1p1 + FLAG_HEIGHT + 3
                    y_flag_t2p1 = y_flag_t1p2 + FLAG_HEIGHT + 3 + 3
                    y_flag_t2p2 = y_flag_t2p1 + FLAG_HEIGHT + 3

                    if t1p1_flag != None:
                        self.canvas.SetImage(t1p1_flag, 0, y_flag_t1p1)

                    if t1p2_flag != None:
                        self.canvas.SetImage(t1p2_flag, 0, y_flag_t1p2)

                    if t2p1_flag != None:
                        self.canvas.SetImage(t2p1_flag, 0, y_flag_t2p1)

                    if t2p2_flag != None:
                        self.canvas.SetImage(t2p2_flag, 0, y_flag_t2p2)

    def display_singles_flags(self, img_t1, img_t2):
        if img_t1 != None:
            y_flag_t1 = max(0, PANEL_HEIGHT/2/2 - img_t1.height/2)
            self.canvas.SetImage(img_t1, 0, y_flag_t1)

        if img_t2 != None:
            y_flag_t2 = max(PANEL_HEIGHT/2, PANEL_HEIGHT/2 + PANEL_HEIGHT/2/2 - img_t2.height/2)
            self.canvas.SetImage(img_t2, 0, y_flag_t2)


    def display_winner(self, match):
        # FIXME winner is not displayed
        b = (0, 0 ,0)
        r = (128, 0, 0)
        y = (255, 215, 0)
        w = (96, 64, 0)
        cup = [
            [b,b,y,y,y,y,y,b,b],
            [w,y,y,y,y,y,y,y,w],
            [w,b,y,y,y,y,y,b,w],
            [w,b,y,y,y,y,y,b,w],
            [b,w,y,y,y,y,y,w,b],
            [b,b,w,y,y,y,w,b,b],
            [b,b,b,y,y,y,b,b,b],
            [b,b,b,b,y,b,b,b,b],
            [b,b,y,y,y,y,y,b,b],
            [b,b,y,y,y,y,y,b,b]]
        match_result = match.get("matchResult", None)
        medal_delta=12
        x_medal=X_SCORE_SERVICE
        if match_result == "T1_WON":
            draw_matrix(self.canvas, cup, x_medal, medal_delta)
        elif match_result == "T2_WON":
            draw_matrix(self.canvas, cup, x_medal, PANEL_HEIGHT / 2 + medal_delta)

    def display_match(self, match):
        # draw_grid(self.canvas, 8, 8, COLOR_GREY_DARKEST)
        self.display_names(match)
        self.display_score(match)
        self.display_winner(match)

    def draw_error_indicator(self):
        x = (0, 0, 0)
        o = (111, 168, 220) # COLOR_BLUE_7c
        dot = [
            [x,o,o,x],
            [o,o,o,o],
            [o,o,o,o],
            [x,o,o,x]]
        draw_matrix(self.canvas, dot, PANEL_WIDTH - 4, PANEL_HEIGHT - 4)

    def display_ebusy_greeting(self, ebusy):
        text = ebusy.get("greeting", "Hello!")
        lines = text.split('\n')
        lines_count = len(lines)

        color = COLOR_BLUE_7c
        h_available = PANEL_HEIGHT
        w_available = PANEL_WIDTH

        prev_y = 0
        for line in lines:
            font = pick_font_that_fits(w_available, h_available, line)
            x = max(0, (w_available - width_in_pixels(font, line)) / lines_count)
            prev_y = y = prev_y + y_font_center(font, h_available / lines_count)
            graphics.DrawText(self.canvas, font, x, y, color, line)

# Main function
if __name__ == "__main__":
    infoboard = SevenCourtsM1()
    if (not infoboard.process()):
        infoboard.print_help()
