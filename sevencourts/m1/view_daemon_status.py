"""
Daemon status overlay — renders BLE connection indicator on top of primary content.

When BLE is connected: bordered box with BT icon + "Connected [to <name>]"
Persistent until BLE disconnects.
"""

from sevencourts.rgbmatrix import *
from sevencourts.m1.dimens import *
from sevencourts.m1.daemon_state import DaemonState


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

COLOR_STATUS_GREEN = COLOR_7C_GREEN
COLOR_BT_BLUE = COLOR_7C_BLUE
COLOR_BORDER = COLOR_7C_DARK_GREY

_BT_ICON_W = 7
_BT_ICON_H = 9


def _draw_bt_icon(cnv, x0: int, y0: int):
    clr = rgb_list(COLOR_BT_BLUE)
    for row_i, row in enumerate(_BT_ICON):
        for col_i, px in enumerate(row):
            if px:
                cnv.SetPixel(x0 + col_i, y0 + row_i, *clr)


def _draw_ble_box(cnv, daemon: DaemonState):
    """BLE connected: bordered box with BT icon and 'Connected [to <name>]'."""
    text = daemon.ble_status
    fnt = FONT_XS

    text_w = width_in_pixels(fnt, text)
    text_h = y_font_offset(fnt)

    pad_x = 3
    pad_y = 2
    icon_gap = 3  # gap between BT icon and text
    inner_w = _BT_ICON_W + icon_gap + text_w
    inner_h = max(_BT_ICON_H, text_h)
    box_w = inner_w + pad_x * 2 + 2  # +2 for 1px border on each side
    box_h = inner_h + pad_y * 2 + 2

    box_x = 2  # 2px from left edge
    box_y = 2  # 2px from top edge

    # Border (1px dark grey) + black fill
    draw_rect(cnv, box_x, box_y, box_w, box_h, COLOR_BORDER, w_border=1, color_fill=COLOR_BLACK)

    # BT icon — vertically centered inside the box
    icon_x = box_x + 1 + pad_x
    icon_y = box_y + 1 + pad_y + (inner_h - _BT_ICON_H) // 2
    _draw_bt_icon(cnv, icon_x, icon_y)

    # Text — vertically centered
    text_x = icon_x + _BT_ICON_W + icon_gap
    text_y = box_y + 1 + pad_y + (inner_h - text_h) // 2 + text_h
    draw_text(cnv, text_x, text_y, text, fnt, COLOR_STATUS_GREEN)


def draw_overlay(cnv, daemon: DaemonState, panel_info: dict):
    """Main entry point — called after primary content is drawn."""
    if daemon.ble_status:
        _draw_ble_box(cnv, daemon)
