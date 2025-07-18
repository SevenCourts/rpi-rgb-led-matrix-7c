## SevenCourts common module
import os
import socket
import gettext
import m1_logging

logger = m1_logging.logger("7c")

LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
# Set up gettext
def setup_i18n(lang='en'):
    try:
        logger.debug(f"Locale dir: {LOCALE_DIR}")
        # Bind the domain to the locale directory for the specified language
        translator = gettext.translation('messages', LOCALE_DIR, languages=[lang], fallback=True)
        # Install the translation, making the '_' function available globally
        translator.install()
        logger.debug(f"Translation for '{lang}' installed")
        return translator
    except FileNotFoundError:
        logger.warn(f"Translation for '{lang}' not found in '{LOCALE_DIR}', using defaults.")
        # If translation files are not found, provide a dummy _ function returning the key
        import builtins
        builtins._ = lambda x: x
        return None


BASE_URL = os.getenv('TABLEAU_SERVER_BASE_URL', 'https://prod.tableau.tennismath.com')

if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    from RGBMatrixEmulator import graphics # type: ignore
else:
    from rgbmatrix import graphics # type: ignore

from PIL import Image
from functools import partial

# FIXME use not hardcoded directory (TBD)
IMAGE_CACHE_DIR = "/opt/7c/cache-images"

# Constants for the 7C M1 panel (P5 192 x 64)
W_PANEL = 192
H_PANEL = 64

W_TILE = int(W_PANEL / 3)  # 64
H_TILE = int(H_PANEL / 2)  # 32

H_FLAG = 12
W_FLAG = 18
W_FLAG_SMALL = int(W_FLAG / 2)  # 9
H_FLAG_SMALL = int(H_FLAG / 2)  # 6

# Style constants
COLOR_WHITE = graphics.Color(255, 255, 255)
COLOR_GREY = graphics.Color(192, 192, 192)
COLOR_GREY_DARK = graphics.Color(96, 96, 96)
COLOR_GREY_DARKEST = graphics.Color(32, 32, 32)
COLOR_BLACK = graphics.Color(0, 0, 0)
COLOR_RED = graphics.Color(255, 0, 0)
COLOR_YELLOW = graphics.Color(255, 255, 0)
COLOR_GREEN = graphics.Color(0, 255, 0)
COLOR_BLUE = graphics.Color(0, 0, 255)

COLOR_7C_GREEN = graphics.Color(147, 196, 125)
COLOR_7C_BLUE = graphics.Color(111, 168, 220)
COLOR_7C_BLUE_DARK = graphics.Color(37, 56, 73)
COLOR_7C_GREEN_DARK = graphics.Color(58, 77, 49)
COLOR_7C_GOLD = graphics.Color(255, 215, 0)

COLOR_SV1845_1 = graphics.Color( int('0xC9', 0), int('0x42', 0), int('0x40', 0))
COLOR_SV1845_2 = graphics.Color( int('0x29', 0), int('0x49', 0), int('0x75', 0))
#COLOR_SV1845_2 = graphics.Color( '#294975')

COLOR_7C_STATUS_ERROR = COLOR_7C_BLUE
COLOR_7C_STATUS_INIT = COLOR_7C_GREEN_DARK

COLOR_DEFAULT = COLOR_GREY
COLOR_CLOCK_DEFAULT = COLOR_WHITE

def load_font(path):
    result = graphics.Font()
    result.LoadFont(path)
    return result


FONT_XXS_SDK = load_font("fonts/tom-thumb.bdf")
FONT_XS_SDK = load_font("fonts/5x8.bdf")
FONT_S_SDK = load_font("fonts/7x13.bdf")
FONT_M_SDK = load_font("fonts/9x15.bdf")
FONT_L_SDK = load_font("fonts/10x20.bdf")
FONT_XL_SDK = load_font("fonts/texgyre-27-modified.bdf")

FONT_XS_SPLEEN = load_font("fonts/spleen-5x8-german-characters/spleen-5x8.bdf")
FONT_S_SPLEEN = load_font("fonts/spleen-2.1.0/spleen-6x12.bdf")
FONT_M_SPLEEN = load_font("fonts/spleen-2.1.0/spleen-8x16.bdf")
FONT_L_SPLEEN = load_font("fonts/spleen-2.1.0/spleen-12x24.bdf")
FONT_XL_SPLEEN = load_font("fonts/spleen-2.1.0/spleen-16x32.bdf")
FONT_XXL_SPLEEN = load_font("fonts/spleen-2.1.0/spleen-32x64.bdf")

FONT_L_7SEGMENT = load_font("fonts/7segment/7segment_26_monospace_digits.bdf")
FONT_XL_7SEGMENT = load_font("fonts/7segment/7segment_45_monospace_digits.bdf")
FONT_XXL_7SEGMENT = load_font("fonts/7segment/7segment_66_monospace_digits.bdf")

# Initial fonts - all from the SDK
FONTS_V0 = [
    FONT_XL_SDK,
    FONT_L_SDK,
    FONT_M_SDK,
    FONT_S_SDK,
    FONT_XS_SDK,
    FONT_XXS_SDK]

# Spleen fonts
FONTS_V1 = [
    FONT_XL_SPLEEN,
    FONT_L_SPLEEN,
    FONT_M_SPLEEN,
    FONT_S_SPLEEN,
    FONT_XS_SPLEEN,
    FONT_XXS_SDK]

# Spleen with a compromise L font
FONTS_V2 = [
    FONT_XL_SPLEEN,
    FONT_L_SDK,
    FONT_M_SPLEEN,
    FONT_S_SPLEEN,
    FONT_XS_SPLEEN,
    FONT_XXS_SDK]

FONTS = FONTS_V1

FONT_XL = FONTS[0]
FONT_L = FONTS[1]
FONT_M = FONTS[2]
FONT_S = FONTS[3]
FONT_XS = FONTS[4]
FONT_XXS = FONTS[5]

FONT_DEFAULT = FONT_S

if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    FONT_CLOCK_DEFAULT = FONT_L
else:
    FONT_CLOCK_DEFAULT = FONT_XL_SDK

Y_FONT_EXTRA_OFFSETS = {
    '-misc-spleen-medium-r-normal--32-320-72-72-C-160-ISO10646-1': 0,
    '-misc-spleen-medium-r-normal--24-240-72-72-C-120-ISO10646-1': 1,
    '-misc-spleen-medium-r-normal--16-160-72-72-C-80-ISO10646-1': 2,
    '-misc-spleen-medium-r-normal--12-120-72-72-C-60-ISO10646-1': 2,
    '-misc-spleen-medium-r-normal--8-80-72-72-C-50-ISO10646-1': 0,
    '-Raccoon-Fixed4x6-Medium-R-Normal--6-60-75-75-P-40-ISO10646-1': 1,
    '-Misc-Fixed-Medium-R-Normal--8-80-75-75-C-50-ISO10646-1': 0,
    '-Misc-Fixed-Medium-R-Normal--13-120-75-75-C-70-ISO10646-1': 0,
    '-Misc-Fixed-Medium-R-Normal--15-140-75-75-C-90-ISO10646-1': 1,
    '-Misc-Fixed-Medium-R-Normal--20-200-75-75-C-100-ISO10646-1': 1,
    '-FreeType-TeX Gyre Adventor-Medium-R-Normal--27-270-72-72-P-151-ISO10646-1': 1
}

Y_FONT_SYMBOL_NORMAL_HEIGHTS = {
    FONT_XL_SDK: 20,
    FONT_L_SDK: 13,
    FONT_M_SDK: 10,
    FONT_S_SDK: 9,
    FONT_XS_SDK: 6,
    FONT_XXS_SDK: 5,

    FONT_XXL_SPLEEN: 40,
    FONT_XL_SPLEEN: 20,
    FONT_L_SPLEEN: 15,
    FONT_M_SPLEEN: 10,
    FONT_S_SPLEEN: 8,
    FONT_XS_SPLEEN: 6,

    FONT_XXL_7SEGMENT: 64,
    FONT_XL_7SEGMENT: 44,
    FONT_L_7SEGMENT: 25
}

H_FONT_XS = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XS)
H_FONT_XXS = Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(FONT_XXS)

def ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        result = s.getsockname()[0]
        s.close()
    except Exception as e:
        logger.exception(e)
        result = "###"
    return result


def y_font_offset(font):
    # This works only on emulator
    # return Y_FONT_EXTRA_OFFSETS.get(font.headers['fontname'], 0) + font.baseline + font.headers['fbbyoff']
    return Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(font)


def y_font_center(font, container_height):
    """Returns y position for the font to be placed vertically centered"""
    y_offset_font = y_font_offset(font)
    return (container_height - y_offset_font) / 2 + y_offset_font


def x_font_center(text, container_width, font):
    """Returns x position for the given text and font to be placed horizontally centered"""
    text_width = 0
    for c in text:
        text_width += font.CharacterWidth(ord(c))
    return max(0, (container_width - text_width) / 2)


def width_in_pixels(font, text):
    result = 0
    if text:
        for c in text:
            result += font.CharacterWidth(ord(c))
    # print('<{}> => {}'.format(text,result))
    return result


def truncate_text(font, max_width, text):
    result = ""
    total_width = 0
    for c in text:
        total_width += font.CharacterWidth(ord(c))
        if total_width <= max_width:
            result += c
        else:
            break
    return result


def _is_font_fits(font, width, height, *texts):
    font_symbol_height = y_font_offset(font)
    max_width_with_this_font = max(map(partial(width_in_pixels, font), *texts))
    # print('{}>={} {}>={} {}'.format(height, font_symbol_height, width, max_width_with_this_font, *texts))

    result = (height >= font_symbol_height) & (width >= max_width_with_this_font)
    return result


def pick_font_that_fits(width, height, *texts):
    if _is_font_fits(FONT_L, width, height, texts):
        result = FONT_L
    elif _is_font_fits(FONT_M, width, height, texts):
        result = FONT_M
    else:
        result = FONT_S

    return result


def _debug_font_info(font, name=''):
    print('Font {} h={} bl={} y_off={}'.format(
        name,
        font.height,
        font.baseline,
        y_font_offset(font)))


def load_flag_image(flag_code):
    try:       
        return Image.open("images/flags/" + (flag_code or "VOID") + ".png").convert('RGB')
    except Exception as e:
        logger.exception(e)
        return Image.open("images/flags/VOID.png").convert('RGB')


def draw_flag(canvas, x, y, flag_code=None, small=False):
    image = load_flag_image(flag_code)
    if small:
        image.thumbnail((W_FLAG_SMALL, H_FLAG_SMALL), Image.LANCZOS)
    canvas.SetImage(image, x, y)


def draw_text(canvas, x: int, y: int, text: str, font=FONT_DEFAULT, color=COLOR_DEFAULT):
    return graphics.DrawText(canvas, font, x, y, color, text)


def draw_grid(canvas, rows=4, cols=4, color=COLOR_GREY_DARKEST):
    x_step_size = int(W_PANEL / cols)
    for i in range(cols):
        x = i * x_step_size
        graphics.DrawLine(canvas, x, 0, x, H_PANEL, color)
    y_step_size = int(H_PANEL / rows)
    for i in range(rows):
        y = i * y_step_size
        graphics.DrawLine(canvas, 0, y, W_PANEL, y, color)


def draw_matrix(canvas, m, x0, y0):
    y = y0
    for row in m:
        x = x0
        for px in row:
            (r, g, b) = px
            canvas.SetPixel(x, y, r, g, b)
            x = x + 1
        y = y + 1


def fill_rect(canvas, x0: int, y0: int, w: int, h: int, color):
    for x in range(x0, x0 + w):
        graphics.DrawLine(canvas, x, y0, x, y0 + h - 1, color)

def round_rect_corners(cnv, x: int, y: int, w: int, h: int, color = COLOR_BLACK):
    fill_rect(cnv, x, y, 1, 1, color)
    fill_rect(cnv, x + w - 1, y, 1, 1, color)
    fill_rect(cnv, x, y + h - 1, 1, 1, color)
    fill_rect(cnv, x + w - 1, y + h - 1, 1, 1, color)


def rgb_list(color):
    """Returns color as a list of RGB values"""
    if isinstance(color, graphics.Color):
        return [color.red, color.green, color.blue]
    elif isinstance(color, (list, tuple)):
        return list(color)
    else:
        raise ValueError("Unsupported color type: {}".format(type(color)))