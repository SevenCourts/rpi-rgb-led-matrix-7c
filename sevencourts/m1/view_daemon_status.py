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

# Bluetooth icon 9x11 pixels (1=on, 0=off)
_BT_ICON = [
    [0, 0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 0, 1, 0, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 0],
]
_BT_ICON_W = 9
_BT_ICON_H = 11

# WiFi icon 13x12 pixels — 3 arcs (1px high, 2px gaps) + cross dot
_WIFI_ICON = [
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],  # outer arc (7px)
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # gap
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # gap
    [1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1],  # middle arc (5px)
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # gap
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # gap
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],  # inner arc (3px)
    [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],  # gap
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # cross top
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],  # cross center
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # cross bottom
]
_WIFI_ICON_W = 13
_WIFI_ICON_H = 11

# -- Colors -----------------------------------------------------------------

COLOR_TEXT = COLOR_WHITE
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
_ICON_GAP = 3  # gap between icon column and text
_ROW_GAP = 6  # vertical gap between rows
_MIN_BOX_H = H_PANEL // 2  # overlay takes at least 50% of screen height
_ICON_COL_W = max(_BT_ICON_W, _WIFI_ICON_W)  # shared icon column width


# -- Icon drawing -----------------------------------------------------------


def _draw_icon(cnv, icon, x0: int, y0: int, color):
    clr = rgb_list(color)
    for row_i, row in enumerate(icon):
        for col_i, px in enumerate(row):
            if px:
                cnv.SetPixel(x0 + col_i, y0 + row_i, *clr)


# -- Rendering --------------------------------------------------------------


def _draw_ble_row(cnv, text: str, fnt, x: int, text_x: int, y_top: int, row_h: int):
    """Draw BLE row: BT icon (centered in icon column) + text."""
    icon_x = x + (_ICON_COL_W - _BT_ICON_W) // 2
    icon_y = y_top + (row_h - _BT_ICON_H) // 2
    _draw_icon(cnv, _BT_ICON, icon_x, icon_y, COLOR_BT_BLUE)

    text_h = y_font_offset(fnt)
    text_y = y_top + (row_h - text_h) // 2 + text_h  # baseline
    draw_text(cnv, text_x, text_y, text, fnt, COLOR_TEXT)


def _wifi_row_color(phase: OverlayPhase):
    if phase == OverlayPhase.WIFI_OK:
        return COLOR_WIFI_OK
    elif phase == OverlayPhase.WIFI_FAIL:
        return COLOR_WIFI_FAIL
    return COLOR_CONNECTING


def _draw_wifi_row(
    cnv,
    text: str,
    fnt,
    phase: OverlayPhase,
    blink: bool,
    x: int,
    text_x: int,
    y_top: int,
    row_h: int,
):
    """Draw WiFi row: WiFi icon (centered in icon column) + text."""
    color = _wifi_row_color(phase)

    # WiFi icon — hide during blink-off for connecting animation
    if phase != OverlayPhase.WIFI_CONNECTING or blink:
        icon_x = x + (_ICON_COL_W - _WIFI_ICON_W) // 2
        icon_y = y_top + (row_h - _WIFI_ICON_H) // 2
        _draw_icon(cnv, _WIFI_ICON, icon_x, icon_y, color)

    text_h = y_font_offset(fnt)
    text_y = y_top + (row_h - text_h) // 2 + text_h  # baseline
    draw_text(cnv, text_x, text_y, text, fnt, COLOR_TEXT)


def draw_overlay(cnv, daemon: DaemonState, panel_info: dict):
    """Main entry point — called after primary content is drawn."""
    phase = daemon.overlay_phase
    if phase == OverlayPhase.HIDDEN:
        return

    fnt = FONT_XS
    text_h = y_font_offset(fnt)
    row_h = max(
        _BT_ICON_H, _WIFI_ICON_H, text_h
    )  # row height = tallest of icon or text

    ble_text = daemon.overlay_ble_text
    wifi_text = daemon.overlay_wifi_text
    has_ble_row = bool(ble_text)
    has_wifi_row = bool(wifi_text)
    num_rows = has_ble_row + has_wifi_row
    if num_rows == 0:
        return

    # --- Compute box dimensions ---
    # Text starts at the same x for both rows: after icon column + gap
    text_col_w = 0
    if has_ble_row:
        text_col_w = max(text_col_w, width_in_pixels(fnt, ble_text))
    if has_wifi_row:
        text_col_w = max(text_col_w, width_in_pixels(fnt, wifi_text))
    inner_w = _ICON_COL_W + _ICON_GAP + text_col_w
    inner_h = row_h * num_rows + _ROW_GAP * (num_rows - 1)

    box_w = inner_w + _PAD_X * 2 + 2  # +2 for 1px border each side
    box_h = max(inner_h + _PAD_Y * 2 + 2, _MIN_BOX_H)

    # --- Draw box ---
    draw_rect(
        cnv,
        _BOX_X,
        _BOX_Y,
        box_w,
        box_h,
        COLOR_BORDER,
        w_border=1,
        color_fill=COLOR_BLACK,
    )

    content_x = _BOX_X + 1 + _PAD_X
    content_y = _BOX_Y + 1 + (box_h - 2 - inner_h) // 2  # vertically center content
    text_x = content_x + _ICON_COL_W + _ICON_GAP  # shared text left edge
    y = content_y

    # --- Row: BLE ---
    if has_ble_row:
        _draw_ble_row(cnv, ble_text, fnt, content_x, text_x, y, row_h)
        y += row_h + _ROW_GAP

    # --- Row: WiFi ---
    if has_wifi_row:
        _draw_wifi_row(
            cnv, wifi_text, fnt, phase, daemon.blink_tick, content_x, text_x, y, row_h
        )
