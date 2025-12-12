#!/usr/bin/env python3

from samplebase import SampleBase
from sevencourts.rgbmatrix import *
from sevencourts.m1.dimens import *
import sevencourts.m1.model as model
import sevencourts.gateway as gateway
import sevencourts.m1.view as v
import sevencourts.openweathermap as openweathermap
import time
from datetime import datetime
import threading as t
import copy
import sevencourts.logging as logging

_log = logging.logger("main")

# shared state
state = model.PanelState()
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
                    state.last_updated_UTC = datetime.now()
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
        global state

        cnv = self.matrix.CreateFrameCanvas()
        state = model.read_from_file()
        _log.debug(f"Saved state:\n{state}")
        state_ui: model.PanelState = None
        while True:
            with panel_info_lock, weather_info_lock:
                if state_ui == state:
                    _log.debug("😴 Panel state unchanged, skipping redraw")
                else:
                    _log.info(f"🔄 New panel state detected, redrawing\n{state}")
                    model.write_to_file(state)
                    state_ui = copy.deepcopy(state)
                    cnv.Clear()
                    try:
                        v.draw(cnv, state)
                    except Exception as ex:
                        # UI loop exception handler: the panel should not go blank and keep working
                        v.draw_error(cnv, ex)
                        _log.error(
                            f"❌❌ Unexpected error during drawing: {str(ex)}", ex
                        )

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
