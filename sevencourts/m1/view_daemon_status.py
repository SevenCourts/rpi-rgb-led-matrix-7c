"""
Daemon status overlay — renders WiFi setup progress on top of primary content.

Phases:
  BLE_CONNECTED   — 1-row box: BT icon + "Connected [to <name>]"
  WIFI_CONNECTING  — 3-row box: "Connected" / SSID / "Connecting..." with amber blink
  WIFI_OK          — 3-row box: "Connected" / SSID / IP address
  WIFI_FAIL        — 3-row box: "WiFi Failed" / SSID / error reason
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

# -- Colors -----------------------------------------------------------------

COLOR_STATUS_GREEN = COLOR_7C_GREEN
COLOR_BT_BLUE = COLOR_7C_BLUE
COLOR_BORDER = COLOR_7C_DARK_GREY
COLOR_SSID = COLOR_GREY  # subdued for SSID row
COLOR_CONNECTING = COLOR_7C_GOLD  # amber for "Connecting..."
COLOR_SUCCESS_DETAIL = COLOR_7C_BLUE  # IP address
COLOR_FAIL_TITLE = COLOR_RED
COLOR_FAIL_DETAIL = COLOR_7C_GOLD  # error reason

# -- Layout constants -------------------------------------------------------

_BOX_X = 2  # 2px from left edge
_BOX_Y = 2  # 2px from top edge
_PAD_X = 3
_PAD_Y = 2
_ICON_GAP = 3  # gap between BT icon and text
_ROW_GAP = 2  # vertical gap between text rows
_INDICATOR_SIZE = 3  # status indicator square size


# -- Icon drawing -----------------------------------------------------------

def _draw_bt_icon(cnv, x0: int, y0: int):
    clr = rgb_list(COLOR_BT_BLUE)
    for row_i, row in enumerate(_BT_ICON):
        for col_i, px in enumerate(row):
            if px:
                cnv.SetPixel(x0 + col_i, y0 + row_i, *clr)


def _draw_indicator(cnv, x: int, y: int, color):
    """Draw a small filled square indicator."""
    clr = rgb_list(color)
    for dy in range(_INDICATOR_SIZE):
        for dx in range(_INDICATOR_SIZE):
            cnv.SetPixel(x + dx, y + dy, *clr)


# -- Phase 1: BLE Connected (single row, unchanged layout) -----------------

def _draw_ble_box(cnv, daemon: DaemonState):
    text = daemon.overlay_text
    fnt = FONT_XS

    text_w = width_in_pixels(fnt, text)
    text_h = y_font_offset(fnt)

    inner_w = _BT_ICON_W + _ICON_GAP + text_w
    inner_h = max(_BT_ICON_H, text_h)
    box_w = inner_w + _PAD_X * 2 + 2  # +2 for 1px border on each side
    box_h = inner_h + _PAD_Y * 2 + 2

    draw_rect(cnv, _BOX_X, _BOX_Y, box_w, box_h, COLOR_BORDER, w_border=1, color_fill=COLOR_BLACK)

    icon_x = _BOX_X + 1 + _PAD_X
    icon_y = _BOX_Y + 1 + _PAD_Y + (inner_h - _BT_ICON_H) // 2
    _draw_bt_icon(cnv, icon_x, icon_y)

    text_x = icon_x + _BT_ICON_W + _ICON_GAP
    text_y = _BOX_Y + 1 + _PAD_Y + (inner_h - text_h) // 2 + text_h
    draw_text(cnv, text_x, text_y, text, fnt, COLOR_STATUS_GREEN)


# -- Phases 2-3: WiFi setup (3-row layout) ---------------------------------

def _draw_wifi_box(cnv, daemon: DaemonState):
    """3-row layout: title row (FONT_M) + SSID row (FONT_S) + detail row (FONT_S)."""
    phase = daemon.overlay_phase
    fnt_title = FONT_M
    fnt_row = FONT_S

    title_h = y_font_offset(fnt_title)
    row_h = y_font_offset(fnt_row)

    # Calculate inner height: BT icon row + SSID row + detail row
    inner_h = max(_BT_ICON_H, title_h) + _ROW_GAP + row_h + _ROW_GAP + row_h
    box_h = inner_h + _PAD_Y * 2 + 2

    # Calculate inner width: widest of the 3 rows
    title_text = daemon.overlay_text
    ssid_text = daemon.overlay_ssid
    detail_text = daemon.overlay_detail

    # Truncate SSID if too long (max ~20 chars in FONT_S)
    max_text_w = 120  # pixels, leaves room for icon and padding
    if width_in_pixels(fnt_row, ssid_text) > max_text_w:
        while width_in_pixels(fnt_row, ssid_text + "...") > max_text_w and len(ssid_text) > 1:
            ssid_text = ssid_text[:-1]
        ssid_text += "..."

    text_start_x = _BT_ICON_W + _ICON_GAP  # text starts after icon + gap
    title_w = text_start_x + width_in_pixels(fnt_title, title_text) + _INDICATOR_SIZE + _ICON_GAP
    ssid_w = text_start_x + width_in_pixels(fnt_row, ssid_text)
    detail_w = text_start_x + width_in_pixels(fnt_row, detail_text)
    inner_w = max(title_w, ssid_w, detail_w)
    box_w = inner_w + _PAD_X * 2 + 2

    # Draw box
    draw_rect(cnv, _BOX_X, _BOX_Y, box_w, box_h, COLOR_BORDER, w_border=1, color_fill=COLOR_BLACK)

    content_x = _BOX_X + 1 + _PAD_X
    content_y = _BOX_Y + 1 + _PAD_Y

    # Row 1: BT icon + title text + status indicator
    icon_y = content_y + (max(_BT_ICON_H, title_h) - _BT_ICON_H) // 2
    _draw_bt_icon(cnv, content_x, icon_y)

    text_x = content_x + _BT_ICON_W + _ICON_GAP
    text_y = content_y + title_h  # baseline
    title_color = COLOR_FAIL_TITLE if phase == OverlayPhase.WIFI_FAIL else COLOR_STATUS_GREEN
    draw_text(cnv, text_x, text_y, title_text, fnt_title, title_color)

    # Status indicator (top-right of box, after title)
    ind_x = content_x + inner_w - _INDICATOR_SIZE
    ind_y = content_y + (max(_BT_ICON_H, title_h) - _INDICATOR_SIZE) // 2
    if phase == OverlayPhase.WIFI_CONNECTING:
        if daemon.blink_tick:
            _draw_indicator(cnv, ind_x, ind_y, COLOR_CONNECTING)
        # else: blink off — don't draw
    elif phase == OverlayPhase.WIFI_OK:
        _draw_indicator(cnv, ind_x, ind_y, COLOR_STATUS_GREEN)
    elif phase == OverlayPhase.WIFI_FAIL:
        _draw_indicator(cnv, ind_x, ind_y, COLOR_FAIL_TITLE)

    # Row 2: SSID
    row2_y = content_y + max(_BT_ICON_H, title_h) + _ROW_GAP + row_h
    draw_text(cnv, text_x, row2_y, ssid_text, fnt_row, COLOR_SSID)

    # Row 3: detail (IP or error reason)
    row3_y = row2_y + _ROW_GAP + row_h
    if phase == OverlayPhase.WIFI_OK:
        detail_color = COLOR_SUCCESS_DETAIL
    elif phase == OverlayPhase.WIFI_FAIL:
        detail_color = COLOR_FAIL_DETAIL
    else:
        detail_color = COLOR_CONNECTING
    draw_text(cnv, text_x, row3_y, detail_text, fnt_row, detail_color)


# -- Entry point ------------------------------------------------------------

def draw_overlay(cnv, daemon: DaemonState, panel_info: dict):
    """Main entry point — called after primary content is drawn."""
    phase = daemon.overlay_phase

    if phase == OverlayPhase.HIDDEN:
        return
    elif phase == OverlayPhase.BLE_CONNECTED:
        _draw_ble_box(cnv, daemon)
    elif phase in (OverlayPhase.WIFI_CONNECTING, OverlayPhase.WIFI_OK, OverlayPhase.WIFI_FAIL):
        _draw_wifi_box(cnv, daemon)
