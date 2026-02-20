"""
Daemon status overlay — renders BLE + WiFi setup status on top of primary content.

Layout:
  BLE_CONNECTED    — 1-row box: [BT] "Connected to <name>"
  WIFI_CONNECTING  — 2-row box: [BT] "Connected to <name>" / [WiFi] "Connecting to MyNet..."
  WIFI_OK          — 2-row box: [BT] "Connected to <name>" / [WiFi] "MyNet  192.168.1.42"
  WIFI_FAIL        — 2-row box: [BT] "Connected to <name>" / [WiFi] "Wrong password"
"""

from sevencourts.rgbmatrix import *
from sevencourts.m1.dimens import *
from sevencourts.m1.daemon_state import DaemonState, OverlayPhase


# -- Icons ------------------------------------------------------------------

# Bluetooth icon 7x9 pixels (1=on, 0=off)
_BT_ICON = [
    [0, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 1, 0],
    [1, 0, 0, 1, 0, 0, 1],
    [0, 1, 0, 1, 0, 1, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 1, 0, 1, 0],
    [1, 0, 0, 1, 0, 0, 1],
    [0, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 1, 0, 0],
]
_BT_ICON_W = 7
_BT_ICON_H = 9

# WiFi icon 9x7 pixels — signal arcs
_WIFI_ICON = [
    [0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0],
]
_WIFI_ICON_W = 9
_WIFI_ICON_H = 7

# -- Colors -----------------------------------------------------------------

COLOR_STATUS_GREEN = COLOR_7C_GREEN
COLOR_BT_BLUE = COLOR_7C_BLUE
COLOR_BORDER = COLOR_7C_DARK_GREY
COLOR_CONNECTING = COLOR_7C_GOLD  # amber for connecting
COLOR_WIFI_OK = COLOR_7C_GREEN
COLOR_WIFI_FAIL = COLOR_RED

# -- Layout constants -------------------------------------------------------

_BOX_X = 2  # 2px from left edge
_BOX_Y = 2  # 2px from top edge
_PAD_X = 3
_PAD_Y = 2
_ICON_GAP = 3  # gap between icon and text
_ROW_GAP = 2  # vertical gap between rows


# -- Icon drawing -----------------------------------------------------------

def _draw_icon(cnv, icon, x0: int, y0: int, color):
    clr = rgb_list(color)
    for row_i, row in enumerate(icon):
        for col_i, px in enumerate(row):
            if px:
                cnv.SetPixel(x0 + col_i, y0 + row_i, *clr)


# -- Rendering --------------------------------------------------------------

def _draw_ble_row(cnv, text: str, fnt, x: int, y_top: int, row_h: int):
    """Draw BLE row: BT icon + text. Returns row height."""
    icon_y = y_top + (row_h - _BT_ICON_H) // 2
    _draw_icon(cnv, _BT_ICON, x, icon_y, COLOR_BT_BLUE)

    text_x = x + _BT_ICON_W + _ICON_GAP
    text_h = y_font_offset(fnt)
    text_y = y_top + (row_h - text_h) // 2 + text_h  # baseline
    draw_text(cnv, text_x, text_y, text, fnt, COLOR_STATUS_GREEN)


def _wifi_row_color(phase: OverlayPhase):
    if phase == OverlayPhase.WIFI_OK:
        return COLOR_WIFI_OK
    elif phase == OverlayPhase.WIFI_FAIL:
        return COLOR_WIFI_FAIL
    return COLOR_CONNECTING


def _draw_wifi_row(cnv, text: str, fnt, phase: OverlayPhase, blink: bool, x: int, y_top: int, row_h: int):
    """Draw WiFi row: WiFi icon + text."""
    color = _wifi_row_color(phase)

    # WiFi icon — hide during blink-off for connecting animation
    if phase != OverlayPhase.WIFI_CONNECTING or blink:
        icon_y = y_top + (row_h - _WIFI_ICON_H) // 2
        _draw_icon(cnv, _WIFI_ICON, x, icon_y, color)

    text_x = x + _WIFI_ICON_W + _ICON_GAP
    text_h = y_font_offset(fnt)
    text_y = y_top + (row_h - text_h) // 2 + text_h  # baseline
    draw_text(cnv, text_x, text_y, text, fnt, color)


def draw_overlay(cnv, daemon: DaemonState, panel_info: dict):
    """Main entry point — called after primary content is drawn."""
    phase = daemon.overlay_phase
    if phase == OverlayPhase.HIDDEN:
        return

    fnt = FONT_XS
    text_h = y_font_offset(fnt)
    row_h = max(_BT_ICON_H, text_h)  # row height = tallest of icon or text
    has_wifi_row = phase in (OverlayPhase.WIFI_CONNECTING, OverlayPhase.WIFI_OK, OverlayPhase.WIFI_FAIL)

    # --- Compute box dimensions ---
    ble_text = daemon.overlay_ble_text
    wifi_text = daemon.overlay_wifi_text

    ble_row_w = _BT_ICON_W + _ICON_GAP + width_in_pixels(fnt, ble_text)
    wifi_row_w = (_WIFI_ICON_W + _ICON_GAP + width_in_pixels(fnt, wifi_text)) if has_wifi_row else 0
    inner_w = max(ble_row_w, wifi_row_w)
    inner_h = row_h + (_ROW_GAP + row_h if has_wifi_row else 0)

    box_w = inner_w + _PAD_X * 2 + 2  # +2 for 1px border each side
    box_h = inner_h + _PAD_Y * 2 + 2

    # --- Draw box ---
    draw_rect(cnv, _BOX_X, _BOX_Y, box_w, box_h, COLOR_BORDER, w_border=1, color_fill=COLOR_BLACK)

    content_x = _BOX_X + 1 + _PAD_X
    content_y = _BOX_Y + 1 + _PAD_Y

    # --- Row 1: BLE ---
    _draw_ble_row(cnv, ble_text, fnt, content_x, content_y, row_h)

    # --- Row 2: WiFi ---
    if has_wifi_row:
        wifi_y = content_y + row_h + _ROW_GAP
        _draw_wifi_row(cnv, wifi_text, fnt, phase, daemon.blink_tick, content_x, wifi_y, row_h)
