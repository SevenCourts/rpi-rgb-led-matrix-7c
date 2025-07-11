# General signage functions

from sevencourts import *

COLOR_BW_VAIHINGEN_ROHR_BLUE = graphics.Color(0x09, 0x65, 0xA6)  # #0965A6

COLOR_SCORE = COLOR_WHITE
COLOR_SCORE_WON = COLOR_WHITE
COLOR_SCORE_LOST = COLOR_GREY

def _color(t1: int, t2: int):
    if (t1==t2):
        return COLOR_SCORE
    elif (t1 > t2):
        return COLOR_SCORE_WON
    else:
        return COLOR_SCORE_LOST

def score_colors(t1: int, t2: int, finished=True):
    if finished and t1 and t2:
        return [_color(t1, t2), _color(t2, t1)]                
    else:
        return [COLOR_SCORE, COLOR_SCORE]
