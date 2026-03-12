import os

_panel_type = os.environ.get("PANEL_TYPE", "M1")

W_PANEL = 192

if _panel_type == "L1":
    H_PANEL = 96
else:  # M1
    H_PANEL = 64

H_FLAG = 12
W_FLAG = 18
W_FLAG_SMALL = W_FLAG // 2  # 9
H_FLAG_SMALL = H_FLAG // 2  # 6
