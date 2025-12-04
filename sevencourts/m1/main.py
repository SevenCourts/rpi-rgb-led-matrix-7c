#!/usr/bin/env python3

from samplebase import SampleBase
from sevencourts.rgbmatrix import *
from sevencourts.m1.dimens import *
from sevencourts.m1.model import PanelState
import sevencourts.gateway as gateway
import sevencourts.m1.view as v
import sevencourts.openweathermap as openweathermap
import time
import threading as t
import copy
import sevencourts.config as cfg
import sevencourts.logging as logging

_log = logging.logger("main")

# shared state
state = PanelState()
state.saved_config = cfg.read()
weather_info_lock = t.Lock()
panel_info_lock = t.Lock()


# Careful with this, since only 60 requests per minute are allowed:
# FIXME get weather info from server
UPDATE_WEATHER_PERIOD_S = 120  # seconds


def _poll_weather_info(period_s: int = UPDATE_WEATHER_PERIOD_S):
    global state
    while True:
        try:
            # FIXME city parameter
            weather_info = openweathermap.fetch_weather(city="Böblingen,DE")
            with weather_info_lock:
                state.weather_info = weather_info
        except:
            pass
        time.sleep(period_s)


def _poll_panel_info(period_s: int = 1):
    global state
    while True:
        panel_id = None
        while panel_id is None:
            try:
                panel_id = gateway.register_panel()
            except Exception as ex:
                _log.error(f"❌ Panel registration failed: {str(ex)}")
                state.server_communication_error = True
                time.sleep(period_s)

        try:
            while True:
                panel_info = gateway.fetch_panel_info(panel_id)
                with panel_info_lock:
                    state.panel_id = panel_id
                    state.panel_info = panel_info
                    state.server_communication_error = False
                time.sleep(period_s)
        except Exception as ex:
            state.server_communication_error = True
            _log.error(f"❌ Cannot fetch panel info: {str(ex)}")
            # _log.debug("Cannot fetch panel info", ex)
        time.sleep(period_s)


def _refresh_time(period_s: int = 1):
    global state
    while True:
        with panel_info_lock:
            state.refresh_time()
        time.sleep(period_s)


class SevenCourtsM1(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SevenCourtsM1, self).__init__(*args, **kwargs)

    def run(self):
        cnv = self.matrix.CreateFrameCanvas()
        state_ui: PanelState = PanelState()
        while True:
            with panel_info_lock, weather_info_lock:
                if state_ui == state:
                    _log.debug("😴 Panel state unchanged, skipping redraw")
                else:
                    _log.info(f"🔄 New panel state detected, redrawing\n{state}")

                    new_config = {"timezone": state.tz()}
                    if new_config != state.saved_config:
                        cfg.write(new_config)
                        state.saved_config = new_config

                    state_ui = copy.deepcopy(state)
                    cnv.Clear()
                    v.draw(cnv, state_ui)
                    cnv = self.matrix.SwapOnVSync(cnv)
            time.sleep(1)  # retry redraw in a second


# Main function
if __name__ == "__main__":

    _log.info("Starting M1 instance")

    # must be daemon to interrupt keyboard (e.g. Ctrl+C)
    t.Thread(target=_refresh_time, daemon=True).start()
    t.Thread(target=_poll_weather_info, daemon=True).start()
    t.Thread(target=_poll_panel_info, daemon=True).start()

    infoboard = SevenCourtsM1()
    if not infoboard.process():
        infoboard.print_help()
