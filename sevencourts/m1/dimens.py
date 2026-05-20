import os

_panel_type = os.environ.get("PANEL_TYPE", "M1")

if _panel_type == "XL1":
    W_PANEL = 320
    H_PANEL = 96
elif _panel_type == "L1":
    W_PANEL = 192
    H_PANEL = 96
else:  # M1
    W_PANEL = 192
    H_PANEL = 64

H_FLAG = 12
W_FLAG = 18
W_FLAG_SMALL = W_FLAG // 2  # 9
H_FLAG_SMALL = H_FLAG // 2  # 6
