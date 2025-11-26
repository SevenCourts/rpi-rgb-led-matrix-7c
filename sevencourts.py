## SevenCourts common module
import os
import socket
import gettext
import m1_logging

from typing import List

logger = m1_logging.logger("7c")

DEFAULT_TIMEZONE = 'Europe/Berlin'

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

setup_i18n('de') # FIXME configuration

BASE_URL = os.getenv('TABLEAU_SERVER_BASE_URL', 'https://prod.tableau.tennismath.com')

if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    from RGBMatrixEmulator import graphics # type: ignore
else:
    from rgbmatrix import graphics # type: ignore

from PIL import Image
from functools import partial

IMAGE_CACHE_DIR = os.getenv('IMAGES_CACHE_DIR', '/opt/7c/cache-images')

# FIXME not all fonts contain this character
# If used with such a font, draw_text call will crash!
SYMBOL_ELLIPSIS = chr(8230) # https://www.compart.com/en/unicode/U+2026

# Constants for the 7C M1 panel (P5 192 x 64)
W_PANEL = 192
H_PANEL = 64

W_TILE = W_PANEL // 3  # 64
H_TILE = H_PANEL // 2  # 32

H_FLAG = 12
W_FLAG = 18
W_FLAG_SMALL = W_FLAG // 2  # 9
H_FLAG_SMALL = H_FLAG // 2  # 6

# Style constants
COLOR_BLACK = graphics.Color(0, 0, 0)
COLOR_WHITE = graphics.Color(255, 255, 255)
COLOR_GREY = graphics.Color(192, 192, 192)
COLOR_GREY_DARK = graphics.Color(96, 96, 96)
COLOR_GREY_DARKEST = graphics.Color(32, 32, 32)

COLOR_RED = graphics.Color(255, 0, 0)
COLOR_GOLD = graphics.Color(255, 215, 0)
COLOR_MAGENTA = graphics.Color(255, 0, 255)

COLOR_YELLOW = graphics.Color(255, 255, 0)
COLOR_GREEN = graphics.Color(0, 255, 0)
COLOR_BLUE = graphics.Color(0, 0, 255)

COLOR_7C_GOLD = graphics.Color(241, 194, 50) #f1c232 - a yellowish color, that is in harmony with this blue #6fa8dc and green #93c47d colors

COLOR_7C_GREY = graphics.Color(50, 50, 50) #323232
COLOR_7C_GREEN = graphics.Color(147, 196, 125) #93c47d
COLOR_7C_BLUE = graphics.Color(111, 168, 220) #6fa8dc

COLOR_7C_DARK_GREY = graphics.Color(23, 23, 23) #171717
COLOR_7C_DARK_GREEN = graphics.Color(58, 77, 49) #3a4d31
COLOR_7C_DARK_BLUE = graphics.Color(37, 56, 73) #253849

COLOR_7C_STATUS_ERROR = COLOR_7C_BLUE
COLOR_7C_STATUS_INIT = COLOR_7C_GREEN
COLOR_7C_STANDBY = COLOR_7C_DARK_GREEN

COLOR_DEFAULT = COLOR_GREY
COLOR_CLOCK_DEFAULT = COLOR_WHITE

def load_font(path) -> graphics.Font:
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


def y_font_offset(font: graphics.Font) -> int:
    # This works only on emulator
    # return Y_FONT_EXTRA_OFFSETS.get(font.headers['fontname'], 0) + font.baseline + font.headers['fbbyoff']
    return Y_FONT_SYMBOL_NORMAL_HEIGHTS.get(font)


def y_font_center(font, container_height):
    """Returns y position for the font to be placed vertically centered"""
    y_offset_font = y_font_offset(font)
    return (container_height - y_offset_font) // 2 + y_offset_font


def x_font_center(text, container_width, font):
    """Returns x position for the given text and font to be placed horizontally centered"""
    text_width = 0
    for c in text:
        text_width += font.CharacterWidth(ord(c))
    return max(0, (container_width - text_width) // 2)


def width_in_pixels(font, text):
    result = 0
    if text:
        for c in text:
            result += font.CharacterWidth(ord(c))
    # print('<{}> => {}'.format(text,result))
    return result

def max_string_length_for_font(font, width) -> int:
    txt = "W" # we assume all used fonts have fixed width
    while width_in_pixels(font, txt) <= width:
        txt += "W"
    return len(txt)-1

def _is_font_fits(font, width, height, *texts) -> bool:
    font_symbol_height = y_font_offset(font)
    max_width_with_this_font = max(map(partial(width_in_pixels, font), *texts))
    #print('{}>={} {}>={} {}'.format(height, font_symbol_height, width, max_width_with_this_font, *texts))

    result = (height >= font_symbol_height) & (width >= max_width_with_this_font)
    return result


def pick_font_that_fits(width, height, *texts) -> graphics.Font:
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
    
def ellipsize(text: str, w_container: int, font: graphics.Font) -> str:
    max_length = max_string_length_for_font(font, w_container)    
    return ellipsize_text(text, max_length)

def ellipsize_text(text: str, max_length: int) -> str:
    
    if len(text) <= max_length:
        return text
    elif len(text) == max_length + 1:
        ellipsis = ''
    else:
        ellipsis = SYMBOL_ELLIPSIS
    return text[:max_length - len(ellipsis)] + ellipsis

def truncate_into_rows(text: str, w_container: int, 
             font: graphics.Font,
             num_rows: int = 2,
             ellipsize: bool = False) -> List[str]:
    max_length = max_string_length_for_font(font, w_container)
    return truncate_text(text, max_length, num_rows, ellipsize)  
    
def truncate_text(text: str, max_length: int, 
                  num_rows: int = 2, 
                  ellipsize: bool = False) -> List[str]:
    words = text.split()
    result = []
    row = ''
    words_counter = 0

    for word in words:
        # truncate or ellipsize words, longer than max_length
        if len(word) > max_length:
            word = ellipsize_text(word, max_length) if ellipsize else word[:max_length]

        if row:
            candidate = row + " " + word
        else:
            candidate = word

        if len(candidate) > max_length:
            result.append(row)
            row = word
        else:
            row = candidate

        if len(result) == num_rows:
            break
        else:
            words_counter += 1

    if row:
        if len(result) < num_rows:
            result.append(row)
        elif ellipsize and len(result) == num_rows:
            result[-1] = result[-1] + ' ' + row
            
    if ellipsize and words_counter < len(words) :
        row = result[-1]
        if len(row) >= max_length:
            row = row[:max_length-1] + SYMBOL_ELLIPSIS
        else:
            row = row + SYMBOL_ELLIPSIS

        result[-1] = row
       
    # Fill up with empty strings
    while len(result) < num_rows:
        result.append('')

    return result


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
    x_step_size = W_PANEL // cols
    for i in range(cols):
        x = i * x_step_size
        graphics.DrawLine(canvas, x, 0, x, H_PANEL, color)
    y_step_size = H_PANEL // rows
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

def draw_rect(canvas, x0: int, y0: int, w: int, h: int, color_border, w_border=1, color_fill=COLOR_BLACK, round_corners=False):
    fill_rect(canvas, x0, y0, w, h, color_border, round_corners)
    
    _x = x0 + w_border
    _w = w - (w_border * 2)
    _y = y0 + w_border
    _h = h - (w_border * 2)
    fill_rect(canvas, _x, _y, _w, _h, color_fill, False)
    if round_corners:
        round_rect_corners(canvas, _x, _y, _w, _h, color_border)

    

def fill_rect(canvas, x0: int, y0: int, w: int, h: int, color, round_corners=False):
    for x in range(x0, x0 + w):
        graphics.DrawLine(canvas, x, y0, x, y0 + h - 1, color)
    if round_corners:
        round_rect_corners(canvas, x0, y0, w, h)

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