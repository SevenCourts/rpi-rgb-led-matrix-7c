#!/usr/bin/env python3

import os
# Set the environment variable USE_RGB_MATRIX_EMULATOR to use with emulator https://github.com/ty-porter/RGBMatrixEmulator
# Do not set to use with real SDK https://github.com/hzeller/rpi-rgb-led-matrix
if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
  from RGBMatrixEmulator import graphics
else:
  from rgbmatrix import graphics

from samplebase import SampleBase
from sevencourts import *
import time
from datetime import datetime
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
COLOR_BW_VAIHINGEN_ROHR_BLUE = graphics.Color(0x09, 0x65, 0xA6) #0965A6
COLOR_BG_COURT_NAME = COLOR_GREY
COLOR_FG_COURT_NAME = COLOR_BLACK
COLOR_FG_PLAYER_NAME = COLOR_GREEN_7c

COLOR_FG_SCORE = COLOR_GREY
COLOR_FG_SCORE_WON = COLOR_WHITE
COLOR_FG_SCORE_LOST = COLOR_GREY_DARK

X_SET1 = 48
X_SET2 = 54
X_SET3 = 60

Y_MARGIN_COURT_T1 = 4        
Y_MARGIN_T1_T2 = 6

ORIENTATION_HORIZONTAL = True
W = PANEL_WIDTH if ORIENTATION_HORIZONTAL else PANEL_HEIGHT
H = PANEL_HEIGHT if ORIENTATION_HORIZONTAL else PANEL_WIDTH

def draw_court_name(canvas, n: int, court_name):
    y = 32 * n
    
    graphics.DrawLine(canvas, 0, y, PANEL_WIDTH, y, COLOR_SEPARATOR_LINE)        
    y += 1
    
    heigth_font_xxs = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XXS)        
    fill_rect(canvas, 0, y, 64, 1+heigth_font_xxs+1, COLOR_BG_COURT_NAME)    
    
    y += heigth_font_xxs + 1
    
    graphics.DrawText(canvas, FONT_XXS, 1, y, COLOR_FG_COURT_NAME, court_name)

def score_color(t1: int, t2: int, finished=True):
    if (finished):
        return COLOR_FG_SCORE_WON if (t1 > t2) else COLOR_FG_SCORE_LOST    
    else:
        return COLOR_FG_SCORE

def draw_match(canvas, n: int, court_name, t1_name, t2_name, t1_set1=-1, t2_set1=-1, t1_set2=-1, t2_set2=-1, t1_set3=-1, t2_set3=-1):

    draw_court_name(canvas, n, court_name)

    heigth_font_xxs = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XXS)        
    y = 32 * n + 1 + heigth_font_xxs + 1 + Y_MARGIN_COURT_T1
    
    y += Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XS)            
    
    graphics.DrawText(canvas, FONT_XS, 0, y, COLOR_FG_PLAYER_NAME, t1_name)
    
    # FIXME finished flag
    if (t1_set3 > -1):
        graphics.DrawText(canvas, FONT_XS, X_SET1, y, score_color(t1_set1, t2_set1), str(t1_set1))
        graphics.DrawText(canvas, FONT_XS, X_SET2, y, score_color(t1_set2, t2_set2), str(t1_set2))
        graphics.DrawText(canvas, FONT_XS, X_SET3, y, score_color(t1_set3, t2_set3, False), str(t1_set3))
    elif (t1_set2 > -1):
        graphics.DrawText(canvas, FONT_XS, X_SET2, y, score_color(t1_set1, t2_set1), str(t1_set1))
        graphics.DrawText(canvas, FONT_XS, X_SET3, y, score_color(t1_set2, t2_set2, False), str(t1_set2))
    elif (t1_set1 > -1):
        graphics.DrawText(canvas, FONT_XS, X_SET3, y, score_color(t1_set1, t2_set1, False), str(t1_set1))
    
    y += Y_MARGIN_T1_T2
    y += Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XS)            
    graphics.DrawText(canvas, FONT_XS, 0, y, COLOR_FG_PLAYER_NAME, t2_name)
    
    if (t2_set3 > -1):
        graphics.DrawText(canvas, FONT_XS, X_SET1, y, score_color(t2_set1, t1_set1), str(t2_set1))
        graphics.DrawText(canvas, FONT_XS, X_SET2, y, score_color(t2_set2, t1_set2), str(t2_set2))
        graphics.DrawText(canvas, FONT_XS, X_SET3, y, score_color(t2_set3, t1_set3, False), str(t2_set3))
    elif (t2_set2 > -1):
        graphics.DrawText(canvas, FONT_XS, X_SET2, y, score_color(t2_set1, t1_set1), str(t2_set1))
        graphics.DrawText(canvas, FONT_XS, X_SET3, y, score_color(t2_set2, t1_set2, False), str(t2_set2))
    elif (t2_set1 > -1):
        graphics.DrawText(canvas, FONT_XS, X_SET3, y, score_color(t2_set1, t1_set1, False), str(t2_set1))

class M1_Demo_Entrance(SampleBase):
    def __init__(self, *args, **kwargs):
        super(M1_Demo_Entrance, self).__init__(*args, **kwargs)        

    def run(self):        
        self.run_demo_entrance()

 
    def show_flags(self, canvas):
        canvas.Clear()

        canvas.SetImage(Image.open("images/flags/france.png").convert('RGB'), 0*18, 0*12)
        canvas.SetImage(Image.open("images/flags/germany.png").convert('RGB'), 1*18, 1*12)
        canvas.SetImage(Image.open("images/flags/italy.png").convert('RGB'), 2*18, 2*12)
        canvas.SetImage(Image.open("images/flags/portugal.png").convert('RGB'), 3*18, 3*12)
        canvas.SetImage(Image.open("images/flags/spain.png").convert('RGB'), 4*18, 0*12)
        canvas.SetImage(Image.open("images/flags/ukraine.png").convert('RGB'), 0*18, 3*12)

        canvas = self.matrix.SwapOnVSync(canvas)        

    def show_centered_text(self, canvas, text, color, font=FONT_XXS):
        canvas.Clear()

        lines = text.split('\n')
        h_total = font.height * len(lines)
        for i in range(len(lines)):
            line = lines[i]
            y = (PANEL_HEIGHT-h_total)/2 + (i+1)*font.height - 2
            line_width = 0
            for c in line:
                line_width+=font.CharacterWidth(ord(c))
            x = max(0, (PANEL_WIDTH-line_width)/2)
            graphics.DrawText(canvas, font, x, y, color, line)
        canvas = self.matrix.SwapOnVSync(canvas)
        

    def run_demo_entrance(self):
    
        canvas = self.matrix.CreateFrameCanvas()
        
        ### lines
        
        
                
        
        ### Title        
        fill_rect(canvas, 0, 0, 64, 32, COLOR_BW_VAIHINGEN_ROHR_BLUE)        
        graphics.DrawText(canvas, FONT_S, 0, 12, COLOR_WHITE, "Stuttgarter")
        graphics.DrawText(canvas, FONT_S, 2, 24, COLOR_WHITE, "Stadtpokal")            
        draw_match(canvas, 1, "1.Stuttgart", "Clement", "Jurikova", 1, 6, 6, 2, 3, 4)
        draw_match(canvas, 2, "2.Brunold Auto", "Seibold", "Schädel", 6, 3, 2, 2)
        draw_match(canvas, 3, "3.Lapp", "Kende", "Kling")
        draw_match(canvas, 4, "4.Egeler", "Mikulslyte", "Radovanovic", 2, 0)
        
        ### Ads        
        y = 160
        canvas.SetImage(Image.open("images/logos/ITF/ITF_64x32_white_bg.png").convert('RGB'), 0, y)
        
        #canvas.SetImage(Image.open("images/logos/ITF/ITF_64x32_grey_bg.png").convert('RGB'), 0, y)
        
        #canvas.SetImage(Image.open("images/logos/ITF/ITF_64x32_transparent_bg.png").convert('RGB'), 0, y)
        
        
        canvas = self.matrix.SwapOnVSync(canvas)
        
        time.sleep(2000)

       


# Main function
if __name__ == "__main__":
    demo = M1_Demo_Entrance()
    if (not demo.process()):
        demo.print_help()
    
