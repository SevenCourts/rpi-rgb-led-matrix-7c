from sevencourts.rgbmatrix import *
from sevencourts.m1.model import PanelState
from sevencourts.m1.dimens import *
import sevencourts.m1.booking.ebusy.view as v_booking_ebusy
import sevencourts.m1.view_scoreboard as v_scoreboard
import sevencourts.m1.view_signage as v_signage

import sevencourts.m1.view_clock as v_clock
import sevencourts.m1.view_message as v_message
import sevencourts.m1.view_image as imgs


def draw(cnv, state: PanelState):
    info = state.panel_info
    if not info:
        _draw_init_screen(cnv, state)
    if info.get("standby"):
        _draw_standby_mode_indicator(cnv, state.time_now)
    elif "booking" in info:
        v_booking_ebusy.draw(cnv, state)
    elif "ebusy-ads" in info:
        v_booking_ebusy.draw_ads(cnv, state)
    elif "idle-info" in info:
        _draw_idle_mode(cnv, info.get("idle-info"), state.time_now)
    elif "signage-info" in info:
        v_signage.draw(cnv, info.get("signage-info"))
    elif "team1" in info:
        v_scoreboard.draw(cnv, info)

    if state.server_communication_error:
        _draw_status_indicator(cnv, COLOR_7C_STATUS_ERROR)


def _draw_init_screen(cnv, state: PanelState, error=False):
    y = y_font_offset(FONT_DEFAULT)
    draw_text(cnv, 0, y, "Connecting to server...", FONT_DEFAULT, COLOR_7C_BLUE)

    v_clock.draw_clock_by_coordinates(
        cnv,
        state.time_now,
        v_clock.W_LOGO_WITH_CLOCK,
        H_PANEL,
        FONT_CLOCK_DEFAULT,
        COLOR_CLOCK_DEFAULT,
    )

    _draw_status_indicator(
        cnv, COLOR_7C_STATUS_ERROR if error else COLOR_7C_STATUS_INIT
    )


def _draw_idle_mode(cnv, idle_info, time_now: str):
    if idle_info.get("image-preset"):
        imgs.draw_preset_image(cnv, idle_info, time_now)
    elif idle_info.get("image-url"):
        imgs.draw_uploaded_image(cnv, idle_info, time_now)
    elif idle_info.get("message"):
        v_message.draw(cnv, idle_info, time_now)
    elif idle_info.get("clock"):
        v_clock.draw_clock(cnv, time_now, idle_info.get("clock"))
    else:
        # Just in case, not to leave the scoreboard completely black
        _draw_standby_mode_indicator(cnv, time_now)


def _draw_standby_mode_indicator(cnv, time_now: str):
    g = (COLOR_7C_STANDBY.red, COLOR_7C_STANDBY.green, COLOR_7C_STANDBY.blue)
    dot = [[g, g], [g, g]]
    draw_matrix(cnv, dot, W_PANEL - 3, H_PANEL - 3)
    v_clock.draw_clock(cnv, time_now, None, COLOR_GREY_DARKEST)


def _draw_status_indicator(cnv, color):
    x = (COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)
    o = (color.red, color.green, color.blue)
    dot = [[x, o, o, x], [o, o, o, o], [o, o, o, o], [x, o, o, x]]
    draw_matrix(cnv, dot, W_PANEL - 4, H_PANEL - 4)
