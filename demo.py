#!/usr/bin/env python3

import os

# Set the environment variable USE_RGB_MATRIX_EMULATOR to use
# with emulator https://github.com/ty-porter/RGBMatrixEmulator
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

Y_SHIFT_T1_CUSTOM = 8
Y_SHIFT_T2_CUSTOM = 2

# Timing defaults
TITLE_DURATION = 3
FRAME_DURATION = 8

if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    FONT_CLOCK = FONT_L
    FONT_SCORE = FONT_L
else:
    FONT_CLOCK = FONTS_V0[0]
    FONT_SCORE = FONTS_V0[0]

COLOR_CLOCK = COLOR_GREY


class M1Demo(SampleBase):
    def __init__(self, *args, **kwargs):
        super(M1Demo, self).__init__(*args, **kwargs)
        self.parser.add_argument("-d", "--duration", help="Duration of each frame, seconds", default=FRAME_DURATION)
        self.parser.add_argument("-t", "--title-duration", help="Duration of title frame, seconds",
                                 default=TITLE_DURATION)

    def run(self):
        duration = int(self.args.duration)
        title_duration = int(self.args.title_duration)
        for x in range(100000):
            self.run_slide_show(duration, title_duration)

    @staticmethod
    def render_score_3_sets(canvas, show_game_score):
        # pseudo score in 3 sets:
        # 7-6 3-6 7-4 *30-15

        color_score_set = COLOR_GREY
        color_score_set_won = COLOR_GREY
        color_score_set_lost = COLOR_GREY_DARK
        font = FONT_SCORE

        y_t1 = 26
        y_t2 = 58
        y_service_delta = 14
        x_game = 163
        x_service = 155

        if show_game_score:
            graphics.DrawText(canvas, font, x_game, y_t2, color_score_set, "15")
            graphics.DrawText(canvas, font, x_game, y_t1, color_score_set, "30")

            b = (0, 0, 0)
            w = (192, 192, 0)
            ball = [
                [b, b, b, b, b],
                [b, b, w, b, b],
                [b, w, w, w, b],
                [w, w, b, w, w],
                [b, w, w, w, b],
                [b, b, w, b, b],
                [b, b, b, b, b]]

            draw_matrix(canvas, ball, x_service, y_t1 - y_service_delta)

            x_service_and_game_delta = 0
        else:
            x_service_and_game_delta = W_PANEL - x_service

        w_set = 20
        x_set1 = 96 + x_service_and_game_delta
        x_set2 = x_set1 + w_set
        x_set3 = x_set2 + w_set

        graphics.DrawText(canvas, font, x_set1, y_t1, color_score_set_won, "7")
        graphics.DrawText(canvas, font, x_set2, y_t1, color_score_set_lost, "3")
        graphics.DrawText(canvas, font, x_set3, y_t1, color_score_set, "5")

        graphics.DrawText(canvas, font, x_set1, y_t2, color_score_set_lost, "6")
        graphics.DrawText(canvas, font, x_set2, y_t2, color_score_set_won, "6")
        graphics.DrawText(canvas, font, x_set3, y_t2, color_score_set, "4")

    @staticmethod
    def render_score_3_sets_custom(canvas):
        # pseudo score in 3 sets:
        # 7-6 3-6 7-4 *30-15

        color_score_set = COLOR_CUSTOM
        color_score_set_won = COLOR_CUSTOM
        color_score_set_lost = COLOR_CUSTOM_DARK
        color_score_game = COLOR_CUSTOM
        font = FONT_XL_CUSTOM

        y_t1 = 26 + Y_SHIFT_T1_CUSTOM
        y_t2 = 58 + Y_SHIFT_T2_CUSTOM
        y_service_delta = 14
        x_game = 163
        x_service = 155

        graphics.DrawText(canvas, font, x_game, y_t2, color_score_set, "15")
        graphics.DrawText(canvas, font, x_game, y_t1, color_score_set, "30")

        b = (0, 0, 0)
        w = (color_score_game.red, color_score_game.green, color_score_game.blue)
        ball = [
            [b, b, w, b, b],
            [w, b, w, b, w],
            [b, w, w, w, b],
            [w, w, w, w, w],
            [b, w, w, w, b],
            [w, b, w, b, w],
            [b, b, w, b, b]]
        draw_matrix(canvas, ball, x_service, y_t1 - y_service_delta)
        x_service_and_game_delta = 0

        w_set = 20
        x_set1 = 96 + x_service_and_game_delta
        x_set2 = x_set1 + w_set
        x_set3 = x_set2 + w_set
        graphics.DrawText(canvas, font, x_set1, y_t1, color_score_set_won, "7")
        graphics.DrawText(canvas, font, x_set2, y_t1, color_score_set_lost, "3")
        graphics.DrawText(canvas, font, x_set3, y_t1, color_score_set, "5")
        graphics.DrawText(canvas, font, x_set1, y_t2, color_score_set_lost, "6")
        graphics.DrawText(canvas, font, x_set2, y_t2, color_score_set_won, "6")
        graphics.DrawText(canvas, font, x_set3, y_t2, color_score_set, "4")

        color_caption = COLOR_CUSTOM_CAPTION
        font_caption = FONT_S
        y_caption = 1 + y_font_offset(font_caption)
        graphics.DrawText(canvas, font_caption, 0, y_caption, color_caption, "MEN'S SINGLES")
        graphics.DrawText(canvas, font_caption, x_set1 + 4, y_caption, color_caption, "1")
        graphics.DrawText(canvas, font_caption, x_set2 + 4, y_caption, color_caption, "2")
        graphics.DrawText(canvas, font_caption, x_set3 + 4, y_caption, color_caption, "3")
        graphics.DrawText(canvas, font_caption, x_game + 2, y_caption, color_caption, "GAME")

    def show_score_singles_with_flags_custom(self, canvas, duration):
        canvas.Clear()

        y_t1 = 26 + Y_SHIFT_T1_CUSTOM
        y_t2 = 58 + Y_SHIFT_T2_CUSTOM
        canvas.SetImage(Image.open("images/flags/switzerland.png").convert('RGB'), 0, 12 + Y_SHIFT_T1_CUSTOM)
        canvas.SetImage(Image.open("images/flags/spain.png").convert('RGB'), 0, 44 + Y_SHIFT_T2_CUSTOM)

        flag_margin_r = 2
        color = COLOR_CUSTOM
        font = FONT_XL_CUSTOM
        graphics.DrawText(canvas, font, W_FLAG + flag_margin_r, y_t1, color, "FED")
        graphics.DrawText(canvas, font, W_FLAG + flag_margin_r, y_t2, color, "NAD")
        self.render_score_3_sets_custom(canvas)
        self.matrix.SwapOnVSync(canvas)
        time.sleep(duration)

    def show_flags(self, canvas, duration):
        canvas.Clear()

        canvas.SetImage(Image.open("images/flags/france.png").convert('RGB'), 0 * 18, 0 * 12)
        canvas.SetImage(Image.open("images/flags/germany.png").convert('RGB'), 1 * 18, 1 * 12)
        canvas.SetImage(Image.open("images/flags/italy.png").convert('RGB'), 2 * 18, 2 * 12)
        canvas.SetImage(Image.open("images/flags/portugal.png").convert('RGB'), 3 * 18, 3 * 12)
        canvas.SetImage(Image.open("images/flags/spain.png").convert('RGB'), 4 * 18, 0 * 12)
        canvas.SetImage(Image.open("images/flags/ukraine.png").convert('RGB'), 0 * 18, 3 * 12)

        self.matrix.SwapOnVSync(canvas)
        time.sleep(duration)

    def show_score_singles_with_flags(self, canvas, show_game_score, duration):
        canvas.Clear()
        y_t1 = 26
        y_t2 = 58
        canvas.SetImage(Image.open("images/flags/switzerland.png").convert('RGB'), 0, 10)
        canvas.SetImage(Image.open("images/flags/spain.png").convert('RGB'), 0, 42)
        flag_margin_r = 2
        color = COLOR_GREY
        font = FONT_XL
        graphics.DrawText(canvas, font, W_FLAG + flag_margin_r, y_t1, color, "FED")
        graphics.DrawText(canvas, font, W_FLAG + flag_margin_r, y_t2, color, "NAD")
        self.render_score_3_sets(canvas, show_game_score)
        self.matrix.SwapOnVSync(canvas)
        time.sleep(duration)

    @staticmethod
    def render_names_doubles(canvas, t1p1, t1p2, t2p1, t2p2):

        max_name_length = max(len(t1p1), len(t1p2), len(t2p1), len(t2p2))
        if max_name_length > 10:
            font = FONT_S
            flag_margin_r = 1
        elif max_name_length > 8:
            font = FONT_S
            flag_margin_r = 2
        elif max_name_length > 6:
            font = FONT_M
            flag_margin_r = 2
        else:
            font = FONT_L
            flag_margin_r = 2

        y_t1p1 = 2 + H_FLAG
        y_t1p2 = y_t1p1 + 2 + H_FLAG
        y_t2p1 = y_t1p2 + 18
        y_t2p2 = y_t2p1 + 2 + H_FLAG

        color_name = COLOR_GREY

        graphics.DrawText(canvas, font, W_FLAG + flag_margin_r, y_t1p1, color_name, t1p1.upper())
        graphics.DrawText(canvas, font, W_FLAG + flag_margin_r, y_t1p2, color_name, t1p2.upper())
        graphics.DrawText(canvas, font, W_FLAG + flag_margin_r, y_t2p1, color_name, t2p1.upper())
        graphics.DrawText(canvas, font, W_FLAG + flag_margin_r, y_t2p2, color_name, t2p2.upper())

    def show_score_doubles_with_flags_long(self, canvas, show_game_score, duration):
        canvas.Clear()

        canvas.SetImage(Image.open("images/flags/italy.png").convert('RGB'), 0, 3)
        canvas.SetImage(Image.open("images/flags/germany.png").convert('RGB'), 0, 3 + H_FLAG + 2)
        canvas.SetImage(Image.open("images/flags/argentina.png").convert('RGB'), 0,
                        3 + H_FLAG + 2 + H_FLAG + 3 + 3)
        canvas.SetImage(Image.open("images/flags/switzerland.png").convert('RGB'), 0,
                        3 + H_FLAG + 2 + H_FLAG + 3 + 3 + H_FLAG + 2)

        self.render_names_doubles(canvas, "Giordano", "Müller", "Álvarez", "Hunziker")

        self.render_score_3_sets(canvas, show_game_score)

        self.matrix.SwapOnVSync(canvas)
        time.sleep(duration)

    def show_score_doubles_with_flags_short(self, canvas, show_game_score, duration):
        canvas.Clear()
        canvas.SetImage(Image.open("images/flags/italy.png").convert('RGB'), 0, 6 + 3)
        canvas.SetImage(Image.open("images/flags/portugal.png").convert('RGB'), 0,
                        6 + 3 + H_FLAG + 2 + H_FLAG + 3 + 3)
        self.render_names_doubles(canvas, "Marino", "Bruno", "Sousa", "Carvalho")
        self.render_score_3_sets(canvas, show_game_score)
        self.matrix.SwapOnVSync(canvas)
        time.sleep(duration)

    def show_score_doubles_with_flags_mixto(self, canvas, show_game_score, duration):
        canvas.Clear()
        canvas.SetImage(Image.open("images/flags/vatican.png").convert('RGB'), 0, 6 + 3)
        canvas.SetImage(Image.open("images/flags/italy.png").convert('RGB'), 0,
                        6 + 3 + H_FLAG + 2 + H_FLAG + 3 + 3)
        self.render_names_doubles(canvas, "Salvatori", "Placidi", "Facchetti", "Galliano")
        self.render_score_3_sets(canvas, show_game_score)
        self.matrix.SwapOnVSync(canvas)
        time.sleep(duration)

    def render_statics_for_announcement(self, canvas, text):
        canvas.Clear()
        self.render_weather(canvas)
        lines = text.split('\n')
        graphics.DrawText(canvas, FONT_M, 2, 20, COLOR_GREY, lines[0])
        graphics.DrawText(canvas, FONT_M, 2, 40, COLOR_GREY, lines[1])
        canvas.SetImage(Image.open("images/clipart/heart_19x16.png").convert('RGB'), 36, 45)
        canvas = self.matrix.SwapOnVSync(canvas)
        return canvas

    def show_clock_with_weather_and_announcement(self, canvas, text, duration):
        self.render_statics_for_announcement(canvas, text)
        # draw statics also on the swapped canvas before starting clock
        self.render_statics_for_announcement(canvas, text)
        self.render_clock(canvas, '%H:%M', 124, 61, 104, 14, FONT_CLOCK, duration)

    def render_statics_for_sponsor_logo(self, canvas, image_path):
        canvas.Clear()
        image = Image.open(image_path).convert('RGB')
        canvas.SetImage(image, 10, 4)
        canvas = self.matrix.SwapOnVSync(canvas)
        return canvas

    def show_clock_with_sponsor_logo(self, canvas, image_path, duration):
        self.render_statics_for_sponsor_logo(canvas, image_path)
        # draw statics also on the swapped canvas before starting clock
        self.render_statics_for_sponsor_logo(canvas, image_path)
        self.render_clock(canvas, '%H:%M:%S', 80, 60, 104, 21, FONT_CLOCK, duration)

    def show_big_clock(self, canvas, duration):
        canvas.Clear()
        self.render_clock(canvas, '%H:%M:%S', 80, 60, 104, 21, FONT_CLOCK, duration)

    def render_statics_for_big_clock_with_weather(self, canvas):
        canvas.Clear()
        self.render_weather(canvas)
        canvas = self.matrix.SwapOnVSync(canvas)
        return canvas

    def show_big_clock_with_weather(self, canvas, duration):
        self.render_statics_for_big_clock_with_weather(canvas)
        # draw statics also on the swapped canvas before starting clock
        self.render_statics_for_big_clock_with_weather(canvas)
        self.render_clock(canvas, '%H:%M:%S', 80, 60, 104, 21, FONT_CLOCK, duration)

    @staticmethod
    def render_weather(canvas):
        x_weather = 134
        y_weather = 2
        image_weather = Image.open("images/weather/sunny_with_clouds_25x20.png").convert('RGB')
        canvas.SetImage(image_weather, x_weather, y_weather)
        graphics.DrawText(
            canvas,
            FONT_M,
            x_weather + image_weather.width + 2,
            y_weather + image_weather.height - 4,
            COLOR_GREY,
            '23°')

    def render_clock(self, canvas, str_format, x, y, w, h, font, duration):
        color_clock = COLOR_GREY_DARK
        for _ in range(duration):
            fill_rect(canvas, x, y - h, w, h, COLOR_BLACK)
            current_time = datetime.now().strftime(str_format)
            graphics.DrawText(canvas, font, x, y, color_clock, current_time)
            canvas = self.matrix.SwapOnVSync(canvas)
            time.sleep(1)

    def show_image_centered(self, canvas, path_to_image, duration):
        canvas.Clear()
        image = Image.open(path_to_image).convert('RGB')

        # center image
        x = max(0, (W_PANEL - image.width) / 2)
        y = max(0, (H_PANEL - image.height) / 2)

        canvas.SetImage(image, x, y)
        self.matrix.SwapOnVSync(canvas)
        time.sleep(duration)

    def show_title_slide(self, canvas, text, duration, font=FONT_XS):
        canvas.Clear()
        image = Image.open("images/logos/sevencourts_192x21.png")
        canvas.SetImage(image.convert('RGB'), 0, 10)
        graphics.DrawText(canvas, font, 5, 55, COLOR_GREY, text)
        self.matrix.SwapOnVSync(canvas)
        time.sleep(duration)

    def show_title_text(self, canvas, text, color, duration, font=FONT_S):
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
        time.sleep(duration)

    def show_fonts(self, canvas, duration):
        canvas.Clear()
        draw_grid(canvas)
        phrase = 'NAD FED 15 A'
        # phrase = '      765*40QABCDEFGHIJKLMNOPQRSTUVWXYZ'
        # phrase = '01530A765*40Q Nadal Federer NAD FED'

        fonts = [FONT_XL, FONT_L, FONT_M, FONT_S, FONT_XS, FONT_XXS]
        fonts = fonts[::-1]  # reversing using list slicing
        colors = [COLOR_GREY, COLOR_RED, COLOR_GREEN, COLOR_7C_BLUE, COLOR_CUSTOM, COLOR_WHITE]

        y = 0
        for i in range(len(fonts)):
            f = fonts[i]
            y += y_font_offset(f)
            # This works only in emulator
            # print('{} => w*h: {}*{} d/a {}/{} {}'.format(
            #    y_font_offset(f),
            #    f.CharacterWidth(ord(' ')), f.height,
            #    f.props['font_ascent'], f.props['font_descent'],                
            #    f.headers['fontname']))
            graphics.DrawText(canvas, f, 0, y, colors[i], phrase)

        self.matrix.SwapOnVSync(canvas)
        time.sleep(duration)

    def run_demo_sequence_english(self, canvas, duration, title_duration):

        # 0. Title slide: SevenCourts logo + slogan
        self.show_title_slide(canvas, "Interactive infoboards for EVERY club", duration)

        # 1.1. Idle mode: sequence of logos of our references        
        self.show_title_text(canvas, "Sponsor, club,\nor tournament logo", COLOR_7C_GREEN, title_duration)

        duration_logo = min(3, duration)
        self.show_image_centered(canvas, "images/logos/a-rete_160x43.png", duration_logo)
        self.show_image_centered(canvas, "images/logos/tom-schilke_192x55.png", duration_logo)
        # self.show_image_centered(canvas, "images/logos/sv1845_64x64.png", duration_logo)

        # 1.2. Idle mode: Clock + Weather + etc.
        self.show_title_text(canvas, "Time, weather,\npersonal greetings, etc.", COLOR_7C_GREEN, title_duration)
        self.show_big_clock_with_weather(canvas, duration)
        self.show_clock_with_weather_and_announcement(canvas, "Happy Wedding Day!\nJohn & Mary", duration)

        # 2.1. Match mode: point-by-point
        self.show_title_text(canvas, "The Grand Slam moment\nfor your club!", COLOR_7C_GREEN, title_duration)
        self.show_score_singles_with_flags(canvas, True, duration)
        self.show_title_text(canvas, "Point-by-point score\n(pro mode)", COLOR_7C_GREEN, title_duration)
        self.show_score_doubles_with_flags_short(canvas, True, duration)
        self.show_score_doubles_with_flags_long(canvas, True, duration)

        # 2.2. Match mode: game-by-game
        self.show_title_text(canvas, "Game-by-game score\n(easy mode)", COLOR_7C_GREEN, title_duration)
        self.show_score_doubles_with_flags_short(canvas, False, duration)

        # 2.3. Match mode: point-by-point custom
        self.show_title_text(canvas, "Customize fonts and colors\nto match your style", COLOR_7C_GREEN, title_duration)
        self.show_score_singles_with_flags_custom(canvas, duration)

        # 3. Some texts
        self.show_title_text(canvas, "See in action\non COURT #1 and #6", COLOR_7C_BLUE, duration)
        self.show_title_text(canvas, "API for integration with\nany scoring, tournament,\nor back-office system",
                             COLOR_7C_GREEN, title_duration)
        self.show_title_text(canvas, "Web & Video\nlive broadcasting", COLOR_7C_BLUE, title_duration)
        self.show_title_text(canvas, "Operate via mobile app\nor a Bluetooth button", COLOR_7C_GREEN, title_duration)
        self.show_title_text(canvas,
                             "SPECIAL PadelTrend PRICE\n\nXS1 399 EUR    M1 999 EUR\n\nAny other size: on request",
                             COLOR_7C_GOLD, duration)

    def run_demo_sequence_italian(self, canvas, duration, title_duration):

        # 0. Title slide: SevenCourts logo + slogan
        self.show_title_slide(canvas, "Tabelloni interattivi per OGNI club", duration * 2)
        self.show_title_text(canvas, "www.sevencourts.com/it", COLOR_7C_GREEN, duration, FONT_M)
        self.show_title_text(canvas, "Vieni a trovarci\na padiglione 4 stand 2", COLOR_7C_BLUE, title_duration, FONT_M)

        # 1.1. Idle mode: sequence of logos of our references
        self.show_title_text(canvas, "Logo dello sponsor,\ndel club o del torneo", COLOR_7C_GREEN, title_duration,
                             FONT_M)

        duration_logo = min(3, duration)
        self.show_image_centered(canvas, "images/logos/pix_115x58.png", duration_logo)
        self.show_image_centered(canvas, "images/logos/decathlon_192x56.png", duration_logo)
        # self.show_image_centered(canvas, "images/logos/a-rete_160x43.png", duration_logo)

        # 1.2. Idle mode: Clock + Weather + etc.
        self.show_title_text(canvas, "Ora, meteo,\nmessaggi di saluto, ecc.", COLOR_7C_GREEN, title_duration, FONT_M)
        # self.show_big_clock_with_weather(canvas, duration)
        self.show_clock_with_weather_and_announcement(canvas, "Felice matrimonio!\nAnna e Marco", duration)

        # 2.1. Match mode: point-by-point
        self.show_title_text(canvas, "Il momento\ndel Grande Slam\nper il tuo club!", COLOR_7C_GREEN, title_duration,
                             FONT_M)
        self.show_score_singles_with_flags(canvas, True, duration)
        # self.show_title_text(canvas, "Punteggio Point-by-point\n(modalità 'Pro')", COLOR_GREEN_7c, title_duration)
        self.show_score_doubles_with_flags_short(canvas, True, duration)
        self.show_score_doubles_with_flags_long(canvas, True, duration)

        # 2.2. Match mode: game-by-game
        # self.show_title_text(canvas, "Punteggio Game-by-game\n(modalità 'Easy')", COLOR_GREEN_7c, title_duration)
        # self.show_score_doubles_with_flags_short(canvas, False, duration)

        # 3. Some texts
        # self.show_title_text(canvas, "Vieni a trovarci\na padiglione 4 stand 2", COLOR_BLUE_7c, duration)
        # self.show_title_text(canvas, "API per l'integrazione\ncon qualsiasi sistema\ndi punteggio,
        # torneo,\no back-office", COLOR_GREEN_7c, title_duration)
        # self.show_title_text(canvas, "Web e video in diretta", COLOR_BLUE_7c, title_duration)
        # self.show_title_text(canvas, "Viene gestito tramite un'app\no un pulsante Bluetooth",
        # COLOR_BLUE_7c, title_duration)
        self.show_title_text(canvas, "PREZZO SPECIALE\n\n999 EUR / 499 EUR", COLOR_7C_GOLD, duration, FONT_M)

    def run_demo_sequence_german(self, canvas, duration, title_duration):

        # 0. Title slide: SevenCourts logo + slogan
        self.show_title_slide(canvas, "Anzeigetafeln für JEDEN Verein", duration, FONT_S)
        self.show_title_text(canvas, "www.sevencourts.com/de", COLOR_7C_GREEN, duration, FONT_M)

        # 1.1. Idle mode: sequence of logos of our references
        self.show_title_text(canvas, "Sponsoren-, Verein-,\noder Turnierlogo",
                             COLOR_7C_GREEN, title_duration, FONT_M)

        duration_logo = min(3, duration)
        self.show_image_centered(canvas, "images/logos/pgpt_192x54.png", duration_logo)
        self.show_image_centered(canvas, "images/logos/tec-waldau_64x64.png", duration_logo)
        self.show_image_centered(canvas, "images/logos/wtb_grey_light_192x49.png", duration_logo)
        self.show_image_centered(canvas, "images/logos/fuerte_61x64.png", duration_logo)
        self.show_image_centered(canvas, "images/logos/tennis-point_bw_192x48.png", duration_logo)

        # 1.2. Idle mode: Clock + Weather + etc.
        self.show_title_text(canvas, "Uhrzeit, Wetter,\nAnkündigungen, u.s.w.", COLOR_7C_GREEN, title_duration, FONT_M)
        self.show_clock_with_weather_and_announcement(canvas, "  Alles Gute!\nAnne und Stefan", duration)

        # 2.1. Match mode: point-by-point
        self.show_title_text(canvas, "Grand-Slam-Moment\nfür deinen Verein!", COLOR_7C_GREEN, title_duration, FONT_M)
        self.show_score_singles_with_flags(canvas, True, duration)
        self.show_score_doubles_with_flags_short(canvas, True, duration)
        self.show_score_doubles_with_flags_long(canvas, True, duration)

        # 2.2. Match mode: game-by-game
        # self.show_title_text(canvas, "Punteggio Game-by-game\n(modalità 'Easy')", COLOR_GREEN_7c, title_duration)
        # self.show_score_doubles_with_flags_short(canvas, False, duration)

        # 3. Some texts
        # self.show_title_text(canvas, "Vieni a trovarci\na padiglione 4 stand 2", COLOR_BLUE_7c, duration)
        # self.show_title_text(canvas, "API per l'integrazione\ncon qualsiasi sistema\ndi punteggio,
        # torneo,\no back-office", COLOR_GREEN_7c, title_duration)
        # self.show_title_text(canvas, "Web e video in diretta", COLOR_BLUE_7c, title_duration)
        # self.show_title_text(canvas, "Viene gestito tramite un'app\no un pulsante Bluetooth",
        # COLOR_BLUE_7c, title_duration)
        self.show_title_text(canvas, "SPEZIALPREIS\n\n999 EUR / 499 EUR", COLOR_7C_GOLD, duration, FONT_M)

    def run_demo_sequence_court_1(self, canvas, duration):
        self.show_image_centered(canvas, "images/logos/padel_trend_expo_119x64.png", duration)
        self.show_clock_with_sponsor_logo(canvas, "images/logos/gimpadel_111x28.png", duration)

    def run_demo_sequence_court_2(self, canvas, duration):
        self.show_image_centered(canvas, "images/logos/padel_trend_expo_119x64.png", duration)
        self.show_clock_with_sponsor_logo(canvas, "images/logos/italgreen_143x28.png", duration)
        self.show_score_doubles_with_flags_mixto(canvas, True, duration)

    def run_slide_show(self, duration, title_duration):
        canvas = self.matrix.CreateFrameCanvas()

        self.run_demo_sequence_german(canvas, duration, title_duration)
        # self.run_demo_sequence_italian(canvas, duration, title_duration)
        # self.run_demo_sequence_english(canvas, duration, title_duration)

        # self.show_flags(canvas, duration)
        # self.show_fonts(canvas, duration)


# Main function
if __name__ == "__main__":
    demo = M1Demo()
    if not demo.process():
        demo.print_help()
