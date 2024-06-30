#!/usr/bin/env python3

import os

# Set the environment variable USE_RGB_MATRIX_EMULATOR to use
# with emulator https://github.com/ty-porter/RGBMatrixEmulator
# Do not set to use with real SDK https://github.com/hzeller/rpi-rgb-led-matrix
if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from samplebase import SampleBase
from sevencourts import *
import time
from PIL import Image

# Style constants
COLOR_CUSTOM = graphics.Color(0, 177, 64)
COLOR_CUSTOM_DARK = graphics.Color(0, 110, 40)
COLOR_CUSTOM_CAPTION = graphics.Color(130, 80, 0)

FONT_XL_CUSTOM = graphics.Font()
FONT_XL_CUSTOM.LoadFont("fonts/RozhaOne-Regular-21.bdf")
FONT_M_CUSTOM = graphics.Font()
FONT_M_CUSTOM.LoadFont("fonts/9x15B.bdf")

if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    FONT_CLOCK = FONT_L
    FONT_SCORE = FONT_L
else:
    FONT_CLOCK = FONTS_V0[0]
    FONT_SCORE = FONTS_V0[0]

COLOR_SEPARATOR_LINE = COLOR_GREY_DARKEST
COLOR_BW_VAIHINGEN_ROHR_BLUE = graphics.Color(0x09, 0x65, 0xA6)  # #0965A6
COLOR_BG_COURT_NAME = COLOR_GREY
COLOR_FG_COURT_NAME = COLOR_BLACK
COLOR_FG_PLAYER_NAME = COLOR_7C_GREEN

COLOR_FG_SCORE = COLOR_GREY
COLOR_FG_SCORE_WON = COLOR_WHITE
COLOR_FG_SCORE_LOST = COLOR_GREY_DARK

X_SET1 = 48
X_SET2 = 54
X_SET3 = 60

Y_MARGIN_COURT_T1 = 4
Y_MARGIN_T1_T2 = 6

ORIENTATION_HORIZONTAL = False
ORIENTATION_VERTICAL = not ORIENTATION_HORIZONTAL

W = W_PANEL if ORIENTATION_HORIZONTAL else H_PANEL
H = H_PANEL if ORIENTATION_HORIZONTAL else W

W_FLAG = 18
H_FLAG = 12

W_FLAG_SMALL = W_FLAG / 2  # 9
H_FLAG_SMALL = H_FLAG / 2  # 6

W_TILE = int(W / 3)  # 64
H_TILE = int(H / 2)  # 32

H_FONT_XS = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XS)
H_FONT_XXS = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XXS)


def draw_court_name(canvas, x: int, y: int, court_name):
    graphics.DrawLine(canvas, x, y, W_PANEL, y, COLOR_SEPARATOR_LINE)
    y += 1
    fill_rect(canvas, x, y, 64, 1 + H_FONT_XXS + 1, COLOR_BG_COURT_NAME)
    y += H_FONT_XXS + 1
    graphics.DrawText(canvas, FONT_XXS, x + 1, y, COLOR_FG_COURT_NAME, court_name)


def score_color(t1: int, t2: int, finished=True):
    if finished:
        return COLOR_FG_SCORE_WON if (t1 > t2) else COLOR_FG_SCORE_LOST
    else:
        return COLOR_FG_SCORE


def draw_match(canvas, n: int, court_name, t1_name, t2_name, t1_set1=-1, t2_set1=-1, t1_set2=-1, t2_set2=-1, t1_set3=-1,
               t2_set3=-1):
    y0 = 32 * n if ORIENTATION_VERTICAL else (0 if n % 2 else H_TILE)
    x0 = 0 if ORIENTATION_VERTICAL else (W_TILE if n < 3 else W_TILE * 2)

    draw_court_name(canvas, x0, y0, court_name)

    y = y0 + 1 + H_FONT_XXS + 1 + Y_MARGIN_COURT_T1 + Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XS)

    graphics.DrawText(canvas, FONT_XS, x0, y, COLOR_FG_PLAYER_NAME, t1_name)

    # FIXME finished flag
    if t1_set3 > -1:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET1, y, score_color(t1_set1, t2_set1), str(t1_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, score_color(t1_set2, t2_set2), str(t1_set2))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t1_set3, t2_set3, False), str(t1_set3))
    elif t1_set2 > -1:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, score_color(t1_set1, t2_set1), str(t1_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t1_set2, t2_set2, False), str(t1_set2))
    elif t1_set1 > -1:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t1_set1, t2_set1, False), str(t1_set1))

    y += Y_MARGIN_T1_T2
    y += Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XS)
    graphics.DrawText(canvas, FONT_XS, x0, y, COLOR_FG_PLAYER_NAME, t2_name)

    if t2_set3 > -1:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET1, y, score_color(t2_set1, t1_set1), str(t2_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, score_color(t2_set2, t1_set2), str(t2_set2))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t2_set3, t1_set3, False), str(t2_set3))
    elif t2_set2 > -1:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, score_color(t2_set1, t1_set1), str(t2_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t2_set2, t1_set2, False), str(t2_set2))
    elif t2_set1 > -1:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t2_set1, t1_set1, False), str(t2_set1))


def draw_match_with_flags(canvas, n: int, court_name, t1_name, t2_name, t1_flag, t2_flag,
                          t1_set1=-1, t2_set1=-1, t1_set2=-1, t2_set2=-1, t1_set3=-1, t2_set3=-1):
    y0 = 32 * n if ORIENTATION_VERTICAL else (0 if n % 2 else H_TILE)
    x0 = 0 if ORIENTATION_VERTICAL else (W_TILE if n < 3 else W_TILE * 2)

    draw_court_name(canvas, x0, y0, court_name)

    h_court_name = H_FONT_XXS + Y_MARGIN_COURT_T1

    y = y0 + 1 + h_court_name + 1

    t1_flag_file = "images/flags/" + t1_flag + ".png"
    display_flag_small(canvas, t1_flag_file, x0, y)

    y += H_FONT_XS
    x = x0 + W_FLAG_SMALL + 1
    w_name_max = W_TILE - W_FLAG_SMALL
    if t1_set3 > -1:
        w_name_max = X_SET1 - 2 - W_FLAG_SMALL
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET1, y, score_color(t1_set1, t2_set1), str(t1_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, score_color(t1_set2, t2_set2), str(t1_set2))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t1_set3, t2_set3, False), str(t1_set3))
    elif t1_set2 > -1:
        w_name_max = X_SET2 - 2 - W_FLAG_SMALL
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, score_color(t1_set1, t2_set1), str(t1_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t1_set2, t2_set2, False), str(t1_set2))
    elif t1_set1 > -1:
        w_name_max = X_SET3 - 2 - W_FLAG_SMALL
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t1_set1, t2_set1, False), str(t1_set1))

    t1_name = truncate_text(FONT_XS, w_name_max, t1_name)
    graphics.DrawText(canvas, FONT_XS, x, y, COLOR_FG_PLAYER_NAME, t1_name)

    y += Y_MARGIN_T1_T2

    t2_flag_file = "images/flags/" + t2_flag + ".png"
    display_flag_small(canvas, t2_flag_file, x0, y)

    y += H_FONT_XS
    x = x0 + W_FLAG_SMALL + 1

    t2_name = truncate_text(FONT_XS, w_name_max, t2_name)
    graphics.DrawText(canvas, FONT_XS, x, y, COLOR_FG_PLAYER_NAME, t2_name)

    if t2_set3 > -1:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET1, y, score_color(t2_set1, t1_set1), str(t2_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, score_color(t2_set2, t1_set2), str(t2_set2))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t2_set3, t1_set3, False), str(t2_set3))
    elif t2_set2 > -1:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET2, y, score_color(t2_set1, t1_set1), str(t2_set1))
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t2_set2, t1_set2, False), str(t2_set2))
    elif t2_set1 > -1:
        graphics.DrawText(canvas, FONT_XS, x0 + X_SET3, y, score_color(t2_set1, t1_set1, False), str(t2_set1))


def draw_tournament_title(canvas, title1, title2, color_fg, color_bg):
    fill_rect(canvas, 0, 0, W_TILE, H_TILE, color_bg)
    graphics.DrawText(canvas, FONT_S, 0, 12, color_fg, title1)
    graphics.DrawText(canvas, FONT_S, 2, 24, color_fg, title2)


def draw_tournament_sponsor(canvas, tick):
    file_image = "images/logos/ITF/ITF_64x32_white_bg.png" if tick % 2 \
        else "images/logos/TC BW Vaihingen-Rohr/tc bw vaihingen-rohr 64x32.png"

    x = 0
    y = H_TILE if ORIENTATION_HORIZONTAL else (H_PANEL - H_TILE)
    canvas.SetImage(Image.open(file_image).convert('RGB'), x, y)


def display_flag(canvas, flag, x, y):
    image = Image.open(flag).convert('RGB')
    canvas.SetImage(image, x, y)


def display_flag_small(canvas, flag, x, y):
    image = Image.open(flag).convert('RGB')
    image.thumbnail((W_FLAG_SMALL, H_FLAG_SMALL), Image.LANCZOS)
    canvas.SetImage(image, x, y)


def display_flags(canvas, flags, grid_w, grid_h):
    canvas.Clear()

    for _x in range(grid_w):
        for _y in range(grid_h):
            i = _x * grid_h + _y
            # log(i)
            x = (1 + W_FLAG_SMALL) * _x
            y = (1 + H_FLAG_SMALL) * _y
            try:
                display_flag(canvas, flags[i], x, y)
            except IndexError as ex:
                log("oops", ex)

    # canvas.SetImage(Image.open("images/flags/france.png").convert('RGB'), 0*18, 0*12)
    # canvas.SetImage(Image.open("images/flags/germany.png").convert('RGB'), 1*18, 1*12)
    # canvas.SetImage(Image.open("images/flags/italy.png").convert('RGB'), 2*18, 2*12)
    # canvas.SetImage(Image.open("images/flags/portugal.png").convert('RGB'), 3*18, 3*12)
    # canvas.SetImage(Image.open("images/flags/spain.png").convert('RGB'), 4*18, 0*12)
    # canvas.SetImage(Image.open("images/flags/ukraine.png").convert('RGB'), 0*18, 3*12)


def display_centered_text(canvas, text, color, font=FONT_XXS):
    lines = text.split('\n')
    h_total = font.height * len(lines)
    for i in range(len(lines)):
        line = lines[i]
        y = (H_PANEL - h_total) / 2 + (i + 1) * font.height - 2
        line_width = 0
        for c in line:
            line_width += font.CharacterWidth(ord(c))
        x = max(0, (W_PANEL - line_width) / 2)
        graphics.DrawText(canvas, font, x, y, color, line)


class M1DemoEntrance(SampleBase):
    def __init__(self, *args, **kwargs):
        super(M1DemoEntrance, self).__init__(*args, **kwargs)

    def run(self):
        tick = 0
        while True:
            self.run_demo_entrance_with_flags(tick)
            tick += 1
            time.sleep(5)

    def show_flags(self, canvas):
        canvas.Clear()

        canvas.SetImage(Image.open("images/flags/france.png").convert('RGB'), 0 * 18, 0 * 12)
        canvas.SetImage(Image.open("images/flags/germany.png").convert('RGB'), 1 * 18, 1 * 12)
        canvas.SetImage(Image.open("images/flags/italy.png").convert('RGB'), 2 * 18, 2 * 12)
        canvas.SetImage(Image.open("images/flags/portugal.png").convert('RGB'), 3 * 18, 3 * 12)
        canvas.SetImage(Image.open("images/flags/spain.png").convert('RGB'), 4 * 18, 0 * 12)
        canvas.SetImage(Image.open("images/flags/ukraine.png").convert('RGB'), 0 * 18, 3 * 12)

        self.matrix.SwapOnVSync(canvas)

    def show_centered_text(self, canvas, text, color, font=FONT_XXS):
        canvas.Clear()

        lines = text.split('\n')
        h_total = font.height * len(lines)
        for i in range(len(lines)):
            line = lines[i]
            y = (H_PANEL - h_total) / 2 + (i + 1) * font.height - 2
            line_width = 0
            for c in line:
                line_width += font.CharacterWidth(ord(c))
            x = max(0, (W_PANEL - line_width) / 2)
            graphics.DrawText(canvas, font, x, y, color, line)
        self.matrix.SwapOnVSync(canvas)

    def run_demo_entrance(self, tick):

        canvas = self.matrix.CreateFrameCanvas()

        draw_tournament_title(canvas, "Stuttgarter", "Stadtpokal", COLOR_WHITE, COLOR_BW_VAIHINGEN_ROHR_BLUE)
        draw_match(canvas, 1, "1.Stuttgart", "Clementenko", "Jurikovanko", 1, 6, 6, 2, 3, 4)
        draw_match(canvas, 2, "2.Brunold Auto", "Seiboldenko", "Schädelstein", 6, 3, 2, 2)
        draw_match(canvas, 3, "3.Lapp", "Kenderenko", "Klingiling", 2, 0)
        draw_match(canvas, 4, "4.Egeler", "Mikulslyte", "Radovanovic")
        draw_tournament_sponsor(canvas, tick)

        self.matrix.SwapOnVSync(canvas)

    def run_demo_entrance_with_flags(self, tick):

        canvas = self.matrix.CreateFrameCanvas()

        draw_tournament_title(canvas, "Stuttgarter", "Stadtpokal", COLOR_WHITE, COLOR_BW_VAIHINGEN_ROHR_BLUE)
        draw_match_with_flags(canvas, 1, "1.Stuttgart", "Clementenko", "Jurikova", "germany", "serbia", 1, 6, 6, 2, 3,
                              4)
        draw_match_with_flags(canvas, 2, "2.Brunold Auto", "Seiboldenko", "Schädel", "germany", "germany", 6, 3, 2, 2)
        draw_match_with_flags(canvas, 3, "3.Lapp", "Köläkäiüißenko", "Kling", "japan", "switzerland", 2, 0)
        draw_match_with_flags(canvas, 4, "4.Egeler", "Mikulslytenko", "Radovanovic", "lithuania", "croatia")
        draw_tournament_sponsor(canvas, tick)

        self.matrix.SwapOnVSync(canvas)

    def run_demo_flags(self, tick):

        canvas = self.matrix.CreateFrameCanvas()

        import glob
        all_flags = glob.glob("images/flags/*.png")
        # 10x5 
        # (10 x (18+1)) = 190
        # (5 x (12+1)) = 65

        grid_w = int(W_PANEL // (W_FLAG_SMALL + 1))
        grid_h = int(H_PANEL // (H_FLAG_SMALL + 1))

        log(grid_w)
        log(grid_h)

        batch_size = grid_w * grid_h
        _from = tick * batch_size
        _to = _from + batch_size

        batch = all_flags[_from:_to]

        display_flags(canvas, batch, grid_w, grid_h)

        self.matrix.SwapOnVSync(canvas)


# Main function
if __name__ == "__main__":
    demo = M1DemoEntrance()
    if not demo.process():
        demo.print_help()
