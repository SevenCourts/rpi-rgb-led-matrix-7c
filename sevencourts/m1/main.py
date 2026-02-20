#!/usr/bin/env python3

from samplebase import SampleBase
from sevencourts.rgbmatrix import *
from sevencourts.m1.dimens import *
import sevencourts.m1.model as model
import sevencourts.gateway as gateway
import sevencourts.m1.view as v
import sevencourts.openweathermap as openweathermap
import sevencourts.m1.daemon_state as daemon_state
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
daemon_state_lock = t.Lock()


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


_DISMISS_TIMEOUT_S = 3.0

# Disconnect reasons that warrant a persistent WiFi error indicator
_PERSISTENT_ERROR_REASONS = {"auth_rejected", "network_not_found", "server_unreachable"}


def _poll_daemon_state(period_s: int = 1):
    global state

    OverlayPhase = daemon_state.OverlayPhase

    # Thread-local tracking (not shared)
    last_net_timestamp = 0
    current_phase = OverlayPhase.HIDDEN
    phase_entered_at = 0.0  # time.monotonic()

    while True:
        try:
            ble = daemon_state.read_ble_state() or daemon_state.BleState()
            net = daemon_state.read_network_state() or daemon_state.NetworkState()

            now = time.monotonic()
            ble_connected = ble.event == "ble_client_connected"

            # --- Determine if we have a fresh network event ---
            net_is_new = net.timestamp > last_net_timestamp and net.event != ""
            if net_is_new:
                last_net_timestamp = net.timestamp

            # --- State machine: compute new overlay phase ---
            new_phase = current_phase
            overlay_text = ""
            overlay_detail = ""
            overlay_ssid = ""

            if current_phase in (OverlayPhase.WIFI_OK, OverlayPhase.WIFI_FAIL):
                # Terminal phases: check timeout first
                if now - phase_entered_at >= _DISMISS_TIMEOUT_S:
                    new_phase = OverlayPhase.HIDDEN
                elif net_is_new and net.event == "connecting":
                    # Retry attempt while result is still showing
                    new_phase = OverlayPhase.WIFI_CONNECTING

            if new_phase == OverlayPhase.HIDDEN or new_phase == OverlayPhase.BLE_CONNECTED:
                # Can transition to any phase based on current events
                if net_is_new:
                    if net.event == "connecting":
                        new_phase = OverlayPhase.WIFI_CONNECTING
                    elif net.event == "connected" and net.interface == "wifi":
                        new_phase = OverlayPhase.WIFI_OK
                    elif net.event == "disconnected":
                        new_phase = OverlayPhase.WIFI_FAIL
                elif ble_connected and new_phase == OverlayPhase.HIDDEN:
                    new_phase = OverlayPhase.BLE_CONNECTED

            elif new_phase == OverlayPhase.WIFI_CONNECTING:
                if net_is_new:
                    if net.event == "connected" and net.interface == "wifi":
                        new_phase = OverlayPhase.WIFI_OK
                    elif net.event == "disconnected":
                        new_phase = OverlayPhase.WIFI_FAIL

            # Track phase transitions
            if new_phase != current_phase:
                current_phase = new_phase
                phase_entered_at = now

            # --- Build display fields per phase ---
            blink_tick = False

            if current_phase == OverlayPhase.BLE_CONNECTED:
                device_name = ble.alias or ble.name
                overlay_text = f"Connected to {device_name}" if device_name else "Connected"

            elif current_phase == OverlayPhase.WIFI_CONNECTING:
                overlay_text = "Connected" if ble_connected else "WiFi"
                overlay_ssid = net.ssid or "WiFi"
                overlay_detail = "Connecting..."
                # Toggle blink each poll cycle
                blink_tick = int(now * 2) % 2 == 0

            elif current_phase == OverlayPhase.WIFI_OK:
                overlay_text = "Connected"
                overlay_ssid = net.ssid or "WiFi"
                overlay_detail = net.ip_address or ""

            elif current_phase == OverlayPhase.WIFI_FAIL:
                overlay_text = "WiFi Failed"
                overlay_ssid = net.ssid or ""
                reason = daemon_state.DISCONNECT_REASONS.get(net.reason, net.reason or "Connection failed")
                overlay_detail = reason

            # --- Persistent WiFi error (outside setup sessions) ---
            wifi_error = (
                net.event == "disconnected"
                and net.interface == "wifi"
                and net.reason in _PERSISTENT_ERROR_REASONS
                and current_phase == OverlayPhase.HIDDEN
            )

            # --- BLE disconnect while in BLE_CONNECTED → dismiss ---
            if current_phase == OverlayPhase.BLE_CONNECTED and not ble_connected:
                current_phase = OverlayPhase.HIDDEN
                overlay_text = ""

            # --- Write to shared state ---
            ds = daemon_state.DaemonState(
                ble=ble,
                network=net,
                overlay_phase=current_phase,
                overlay_text=overlay_text,
                overlay_detail=overlay_detail,
                overlay_ssid=overlay_ssid,
                blink_tick=blink_tick,
                wifi_error=wifi_error,
            )

            with daemon_state_lock:
                state.daemon = ds

        except Exception as ex:
            _log.error(f"Daemon state poll error: {ex}")

        time.sleep(period_s)


class SevenCourtsM1(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SevenCourtsM1, self).__init__(*args, **kwargs)

    def run(self):
        global state

        cnv = self.matrix.CreateFrameCanvas()
        state = model.read_from_file()
        state.panel_id = None  # force re-registration on panel restart

        _log.debug(f"Saved state:\n{state}")
        state_ui: model.PanelState = None
        while True:
            with panel_info_lock, weather_info_lock, daemon_state_lock:
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
                            f"❌❌ Unexpected error during drawing: {str(ex)}",
                            exc_info=True,
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
    t.Thread(target=_poll_daemon_state, daemon=True).start()

    infoboard = SevenCourtsM1()
    if not infoboard.process():
        infoboard.print_help()
