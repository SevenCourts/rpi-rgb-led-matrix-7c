#!/usr/bin/env python3

import os
from sevencourts import *

# Set the environment variable USE_RGB_MATRIX_EMULATOR to use with
# emulator https://github.com/ty-porter/RGBMatrixEmulator
# Do not set to use with real SDK https://github.com/hzeller/rpi-rgb-led-matrix
if USE_RGB_MATRIX_EMULATOR:
    from RGBMatrixEmulator import graphics # type: ignore
else:
    from rgbmatrix import graphics # type: ignore
from samplebase import SampleBase

import m1_booking_ebusy
import m1_signage_horizontal as m1_signage
import m1_clock
import m1_message
import m1_image
import m1_scoreboard
import time
import urllib.request
import json
import socket
import network_utils
import subprocess
from datetime import datetime
from dateutil import tz

logger = m1_logging.logger()

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

PANEL_CONFIG_FILE = os.getenv('PANEL_CONFIG')

PANEL_NAME = socket.gethostname()

REGISTRATION_URL = BASE_URL + "/panels/"

def panel_info_url(panel_id):
    return BASE_URL + "/panels/" + panel_id + "/match"


def uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            return float(f.readline().split()[0])
    except Exception as ex:
        logger.debug('Cannot get uptime')
        return -1


# FIXME wtf?! without this call, getting CPU temperature fails when is called from within class instance
try:
    from gpiozero import CPUTemperature # type: ignore
    print(CPUTemperature().temperature)
except Exception as ex:
    logger.debug('Cannot get initial CPU temperature')


def _cpu_temperature():
    try:
        from gpiozero import CPUTemperature # type: ignore
        return CPUTemperature().temperature
    except Exception as ex:
        logger.debug('Cannot get CPU temperature')
        return -1


def _register(url):
    data = json.dumps({"code": PANEL_NAME, "ip": network_utils.ip_address(), "firmware_version": GIT_COMMIT_ID}).encode('utf-8')
    request = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(request, timeout=network_utils.NETWORK_TIMEOUT_SECONDS) as response:
        _json = json.loads(response.read().decode('utf-8'))
        logger.debug(f"Registered: {url} - '{_json}'")
        return _json["id"]


def _fetch_panel_info(panel_id):
    url = panel_info_url(panel_id)
    req = urllib.request.Request(url)
    req.add_header('7C-Is-Panel-Preview', 'false') # FIXME is to be set to 'true' when started as emulator within panel admin web UI
    req.add_header('7C-Uptime', str(uptime()))
    req.add_header('7C-CPU-Temperature', str(_cpu_temperature()))
    with urllib.request.urlopen(req, timeout=network_utils.NETWORK_TIMEOUT_SECONDS) as response:
        logger.debug(f"url='{url}', status={str(response.status)}")
        if response.status == 200:
            match = json.loads(response.read().decode('utf-8'))
            logger.debug(f"match: {match}")
            return match or None  # FIX: the server can return False if match is over, this leads to error then
        elif response.status == 205:
            idle_info = json.loads(response.read().decode('utf-8') or 'null')
            logger.debug(f"idle-info: {idle_info}")
            return idle_info
    return None

def _read_startup_config():
    logger.debug(f"Reading config from '{PANEL_CONFIG_FILE}'")
    result = {}
    if PANEL_CONFIG_FILE:
        lines = []
        try:
            with open(PANEL_CONFIG_FILE, 'r') as file:
                lines = list(filter(lambda x: len(x.strip()) > 0, file.read().splitlines()))
        except:
            pass
        if lines:
            result = {k: v for k, v in map(lambda x: x.split('=', 1), lines)}
    logger.info(f"Config: '{result}'")
    return result

def _write_startup_config(startup_config):
    logger.debug(f"Writing config to '{PANEL_CONFIG_FILE}'")
    if PANEL_CONFIG_FILE:
        conf = []
        for k, v in startup_config.items(): conf.append(k + '=' + str(v))
        try:
            with open(PANEL_CONFIG_FILE, 'w') as file:
                file.write('\n'.join(conf))
        except:
            pass

class SevenCourtsM1(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SevenCourtsM1, self).__init__(*args, **kwargs)
        self.last_known_club_mode = None # FIXME review
        self.last_known_club_mode_arg = None # FIXME review
        self.panel_info = {} #evaluates to boolean False
        self.startup_config = _read_startup_config()
        
    def run(self):
        logger.info("Starting M1 instance")
        
        self.canvas = self.matrix.CreateFrameCanvas()

        self._display_init_screen()

        while True:
            panel_id = self._register()
            try:
                while True:
                    panel_info = _fetch_panel_info(panel_id)
                    if panel_info:
                        self.panel_info = panel_info
                    self.panel_info_failed = False
                    
                    cfg = {"timezone": self._panel_tz()}
                    if (cfg != self.startup_config):
                        _write_startup_config(cfg)
                        self.startup_config = cfg

                    self._display_panel_info()
                    time.sleep(1)
            except Exception as ex:
                self._draw_status_indicator(COLOR_7C_STATUS_ERROR)
                self.panel_info_failed = True
                logger.error(f"Cannot refresh panel: {str(ex)}")
                logger.debug(f"Cannot refresh panel", ex)
            time.sleep(1)

    
    def _register(self):
        """Return panel_id when registration is successful, blocks until success."""
        result = None
        while result is None:
            try:
                logger.debug(f"Registering panel at: {REGISTRATION_URL}")
                result = _register(REGISTRATION_URL)
            except Exception as ex:
                logger.error(f"Panel registration call to '{REGISTRATION_URL}' failed: {str(ex)}")
                if self.panel_info:
                    logger.debug("Displaying the panel info from the last known successful state")
                    self._display_panel_info(True, display_available_networks = False)
                else:
                    logger.debug("Displaying init screen")
                    self._display_init_screen(offline=True, display_available_networks = True)

                time.sleep(1)
        return result

    def _display_init_screen(self, offline=False, display_available_networks=False):
        self.canvas.Clear()

        x = 2
        y = 2 + y_font_offset(FONT_S)
        draw_text(self.canvas, x, y, f"Initializing{SYMBOL_ELLIPSIS}", FONT_S, COLOR_7C_GREEN)

        dt = datetime.now(tz.gettz(self._panel_tz()))
        text = dt.strftime('%H:%M')
        x = m1_clock.W_LOGO_WITH_CLOCK
        y = 62
        draw_text(self.canvas, x, y, text, FONT_CLOCK_DEFAULT, COLOR_CLOCK_DEFAULT)
        if offline:
            self._draw_offline_status(display_available_networks)
        else:
            self._draw_status_indicator(COLOR_7C_STATUS_INIT)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
    
    def _draw_offline_status(self, display_available_networks=False):

        if display_available_networks:
            x = 3
            y = 2 + y_font_offset(FONT_S)
            active_interfaces = network_utils.get_active_interfaces()
            if not active_interfaces:
                self._draw_status_indicator(COLOR_RED, y=0)
                logger.warning("No active network interfaces found (excluding loopback).")
            else:
                y += y_font_offset(FONT_XXS) + 2
                for iface in active_interfaces:
                    logger.info(f"Interface: {iface} is on: Yes (Detected as UP)")

                    iface_type = network_utils.get_interface_type(iface)
                    logger.info(f"Interface: {iface} type: {iface_type}")

                    if iface_type == "WLAN":
                        ssid = network_utils.get_wlan_ssid(iface)
                        logger.info(f"Interface: {iface} WLAN Name (SSID): {ssid}")
                        graphics.DrawText(self.canvas, FONT_XXS, x, y, COLOR_7C_STATUS_ERROR, 
                                            f"{iface} SSID: {ssid}")
                    else:
                        logger.warning(f"Interface: {iface} WLAN Name (SSID): N/A (Not a WLAN interface)")                        
                        
                    y += y_font_offset(FONT_XXS) + 2

        
        # Checking Internet and Server Accessibility
        color_error_indicator = None
        if network_utils.check_internet_access():
            if network_utils.check_server_access(BASE_URL):
                color_error_indicator = COLOR_GREEN
                # should not happen in offline state
                logger.info(f"SevenCourts server is accessible: {BASE_URL}")                
            else:
                color_error_indicator = COLOR_YELLOW
                logger.warning(f"SevenCourts server in NOT accessible: {BASE_URL}")
                if display_available_networks:
                    graphics.DrawText(self.canvas, FONT_XXS, 2, y, color_error_indicator, 
                                            f"SevenCourts server in NOT accessible:")
                    graphics.DrawText(self.canvas, FONT_XXS, 2, y + 2 + y_font_offset(FONT_XXS), color_error_indicator,
                                            BASE_URL)

        else:
            color_error_indicator = COLOR_RED
            logger.warning(f"Internet is NOT accessible")
            if display_available_networks:
                graphics.DrawText(self.canvas, FONT_XXS, 2, y, color_error_indicator,
                                            "No Internet connection.")

        self._draw_status_indicator(color_error_indicator)


    def _display_panel_info(self, offline=False, display_available_networks=False):
        self.canvas.Clear()

        if self.panel_info.get('standby'):
            self._draw_standby_mode_indicator()
        elif 'booking' in self.panel_info:
            m1_booking_ebusy.draw_booking(self.canvas, self.panel_info.get('booking'), self._panel_tz())
        elif 'ebusy-ads' in self.panel_info:
            m1_booking_ebusy.draw_ebusy_ads(self.canvas, self.panel_info.get('ebusy-ads'))
        elif 'idle-info' in self.panel_info:
            self._draw_idle_mode(self.panel_info.get('idle-info'))
        elif 'signage-info' in self.panel_info:
            m1_signage.draw_tournament(self.canvas, self.panel_info.get('signage-info'))
        elif 'team1' in self.panel_info:
            m1_scoreboard.draw_match(self.canvas, self.panel_info)

        if offline:
            self._draw_offline_status(display_available_networks)

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def _draw_idle_mode(self, idle_info):
        if idle_info.get('image-preset'):
            m1_image.draw_idle_mode_image_preset(self.canvas, idle_info, self._panel_tz())
        elif idle_info.get('image-url'):
            m1_image.draw_idle_mode_image_url(self.canvas, idle_info, self._panel_tz())
        elif idle_info.get('message'):
            m1_message.draw_idle_mode_message(self.canvas, idle_info, self._panel_tz())
        elif idle_info.get('clock'):
            m1_clock.draw_clock(self.canvas, idle_info.get('clock'), self._panel_tz())
        else:
            # Just in case, not to leave the scoreboard completely black
            self._draw_standby_mode_indicator()

    def _draw_standby_mode_indicator(self):
        g = (COLOR_7C_GREEN_DARK.red, COLOR_7C_GREEN_DARK.green, COLOR_7C_GREEN_DARK.blue)
        dot = [
            [g, g],
            [g, g]]
        draw_matrix(self.canvas, dot, W_PANEL - 3, H_PANEL - 3)
        m1_clock.draw_clock(self.canvas, True, self._panel_tz(), COLOR_GREY_DARKEST)


    def _draw_status_indicator(self, color, x = (W_PANEL - 4), y = (H_PANEL - 4)):
        b = (COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)
        c = (color.red, color.green, color.blue)
        dot = [
            [b, c, c, b],
            [c, c, c, c],
            [c, c, c, c],
            [b, c, c, b]]
        draw_matrix(self.canvas, dot, x, y)

    def _panel_tz(self):
        return self.panel_info.get('idle-info', {}).get('timezone', self.startup_config.get('timezone', 'Europe/Berlin'))


# Main function
if __name__ == "__main__":
    infoboard = SevenCourtsM1()
    if not infoboard.process():
        infoboard.print_help()
