#!/usr/bin/env python3

import os

# Set the environment variable USE_RGB_MATRIX_EMULATOR to use with
# emulator https://github.com/ty-porter/RGBMatrixEmulator
# Do not set to use with real SDK https://github.com/hzeller/rpi-rgb-led-matrix
if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    from RGBMatrixEmulator import graphics
else:
    from rgbmatrix import graphics

from samplebase import SampleBase
from sevencourts import *
import m1_booking_ebusy
import m1_signage_horizontal as m1_signage
import m1_signage_vertical
import m1_clock
import m1_message
import m1_image

import time
import urllib.request
import json
import socket
import logging
import subprocess
from datetime import datetime

# In container there is no git binary and history -- read from file.
# In local environment we don't want generate this file manually -- ask git.
try:
    with open('commit-id', 'r') as file:
        GIT_COMMIT_ID = file.read().strip()
except:
    GIT_COMMIT_ID = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()

os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
# The default 0o777 does not work,
# see https://stackoverflow.com/questions/5231901/permission-problems-when-creating-a-dir-with-os-makedirs-in-python
os.chmod(IMAGE_CACHE_DIR, 0o777)

PANEL_CONFIG = os.getenv('PANEL_CONFIG')

PANEL_NAME = socket.gethostname()



REGISTRATION_URL = BASE_URL + "/panels/"

PANEL_ID = os.getenv('TABLEAU_PANEL_ID')


def panel_info_url(panel_id):
    return BASE_URL + "/panels/" + panel_id + "/match"


def uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            return float(f.readline().split()[0])
    except Exception as ex:
        log(ex, 'Cannot get uptime')
        return -1


# FIXME wtf?! without this call, getting CPU temperature fails when is called from within class instance
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


class SevenCourtsM1(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SevenCourtsM1, self).__init__(*args, **kwargs)
        self.last_known_club_mode = None
        self.last_known_club_mode_arg = None
        self.panel_info = {}
        self.panel_info_failed = False
        self.registration_failed = False
        self._read_startup_config()

    def _read_startup_config(self):
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

    def _write_startup_config(self):
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
            m1_signage.display_match(self.canvas, 0, "Court #1", [["Shapovalov", "ukraine"]], [["Federer", "switzerland"]],
                                                        [[6, 4], [2, 6], [6, 6]], [9, 7], True)
            m1_signage.display_match(self.canvas, 1, "Court #2", [["Seles", "usa"], ["Graf", "germany"]], [["Sánchez Vicario", "spain"], ["Sabatini", "argentina"]],
                                                        [[1, 2], [2, 6], [6, 6]], ["40", "Ad"], False)
            m1_signage.display_match(self.canvas, 2, "Court #3", None, None, None, None, None)
            m1_signage.display_match_upcoming(self.canvas, 3, "Cupra", [["Nadal", "spain"]], [["Roddick", "usa"]],
                                                         "14:00")
            
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            """
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
            """
            time.sleep(1)


    def _register(self):
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
                        self._display_panel_info()
                    else:
                        self._display_init_screen()

                    time.sleep(1)
                else:
                    self.registration_failed = False
                    return panel_id


    def _display_panel_info(self):
        self.canvas.Clear()

        if self.registration_failed or self.panel_info_failed:
            self._display_error_indicator(self.panel_info.get('standby'))

        if self.panel_info.get('standby'):
            self._display_standby_mode_indicator()
        elif 'booking' in self.panel_info:
            m1_booking_ebusy.display_booking(self.canvas, self.panel_info.get('booking'), self._panel_tz())
        elif 'ebusy-ads' in self.panel_info:
            m1_booking_ebusy.display_ebusy_ads(self.canvas, self.panel_info.get('ebusy-ads'))
        elif 'idle-info' in self.panel_info:
            self._display_idle_mode()
        elif 'tournament-name' in self.panel_info:
            m1_signage_vertical.display_signage_itftournament(self.canvas, self.panel_info.get("courts"), 
                                                              self.panel_info.get("tournament-name"))
        elif 'team1' in self.panel_info:
            self.display_match()

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def _display_idle_mode(self):
        idle_info = self.panel_info.get('idle-info')
        if idle_info.get('image-preset'):
            m1_image.display_idle_mode_image_preset(self.canvas, idle_info, self._panel_tz())
        elif idle_info.get('image-url'):
            m1_image.display_idle_mode_image_url(self.canvas, idle_info, self._panel_tz())
        elif idle_info.get('message'):
            m1_message.display_idle_mode_message(self.canvas, idle_info, self._panel_tz())
        elif idle_info.get('clock'):
            m1_clock.display_clock(self.canvas, idle_info.get('clock'), self._panel_tz())            
        else:
            self._display_standby_mode_indicator()

    def _display_init_screen(self):
        self.canvas.Clear()
        dt = datetime.now()
        text = dt.strftime('%H:%M')
        # FIXME strange dependency on m1_clock
        x = m1_clock.W_LOGO_WITH_CLOCK if ORIENTATION_HORIZONTAL else (x_font_center(text, W_PANEL, m1_clock.FONT_CLOCK))
        y = 62 if ORIENTATION_HORIZONTAL else H_PANEL - 2
        draw_text(self.canvas, x, y, text, m1_clock.FONT_CLOCK, m1_clock.COLOR_CLOCK)
        self._display_error_indicator()
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def _display_standby_mode_indicator(self):
        g = (COLOR_7C_GREEN_DARK.red, COLOR_7C_GREEN_DARK.green, COLOR_7C_GREEN_DARK.blue)
        dot = [
            [g, g],
            [g, g]]
        draw_matrix(self.canvas, dot, W_PANEL - 3, H_PANEL - 3)


    def _display_error_indicator(self, standby=False):
        x = (COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)
        o = (
            COLOR_7C_BLUE_DARK.red if standby else COLOR_7C_BLUE.red,
            COLOR_7C_BLUE_DARK.green if standby else COLOR_7C_BLUE.green,
            COLOR_7C_BLUE_DARK.blue if standby else COLOR_7C_BLUE.blue
        )
        dot = [
            [x, o, o, x],
            [o, o, o, o],
            [o, o, o, o],
            [x, o, o, x]]
        draw_matrix(self.canvas, dot, W_PANEL - 4, H_PANEL - 4)

    def _panel_tz(self):
        return self.panel_info.get('idle-info', {}).get('timezone', 'Europe/Berlin')


# Main function
if __name__ == "__main__":
    infoboard = SevenCourtsM1()
    if not infoboard.process():
        infoboard.print_help()
