import os

from sevencourts.rgbmatrix import FONT_XL_SDK, FONT_XL_7SEGMENT

_panel_type = os.environ.get("PANEL_TYPE", "M1")

if _panel_type == "XL1":
    W_PANEL = 320
    H_PANEL = 96
    W_FLAG = 27
    H_FLAG = 18
    W_LOGO_WITH_CLOCK = 160
    FONT_CLOCK_DEFAULT = FONT_XL_7SEGMENT
elif _panel_type == "L1":
    W_PANEL = 192
    H_PANEL = 96
    # L1 and XL1 share flag size because both panels are 96 px tall.
    W_FLAG = 27
    H_FLAG = 18
    W_LOGO_WITH_CLOCK = 120
    FONT_CLOCK_DEFAULT = FONT_XL_SDK
else:  # M1
    W_PANEL = 192
    H_PANEL = 64
    W_FLAG = 18
    H_FLAG = 12
    W_LOGO_WITH_CLOCK = 120
    FONT_CLOCK_DEFAULT = FONT_XL_SDK

W_FLAG_SMALL = W_FLAG // 2
H_FLAG_SMALL = H_FLAG // 2
