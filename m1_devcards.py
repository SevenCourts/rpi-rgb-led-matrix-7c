from sevencourts import *
import m1_clock

COLOR_MESSAGE = COLOR_7C_BLUE

def draw_all_fonts_with_ellipsis(cnv):
    
    
    
    fonts = {
        "FONT_XXS_SDK": FONT_XXS_SDK,
        "FONT_XS_SDK": FONT_XS_SDK,
        "FONT_S_SDK": FONT_S_SDK,
        "FONT_M_SDK": FONT_M_SDK,
        "FONT_L_SDK": FONT_L_SDK,
        "FONT_XL_SDK": FONT_XL_SDK, # bug in font - badly shown in emulator
        "FONT_XS_SPLEEN": FONT_XS_SPLEEN,
        "FONT_S_SPLEEN": FONT_S_SPLEEN,
        "FONT_M_SPLEEN": FONT_M_SPLEEN,
        "FONT_XXL_SPLEEN": FONT_XXL_SPLEEN,
        "FONT_XL_SPLEEN": FONT_XL_SPLEEN,
        "FONT_L_SPLEEN": FONT_L_SPLEEN,
        "FONT_L_7SEGMENT": FONT_L_7SEGMENT,
        "FONT_XL_7SEGMENT": FONT_XL_7SEGMENT,
        "FONT_XXL_7SEGMENT": FONT_XXL_7SEGMENT
    }

    x = 0
    y = 0
    w_max_in_column = 0
    i = 0
    for name, font in fonts.items():
        i += 1
        w = width_in_pixels(font, "0")
        
        h = y_font_offset(font)

        _i = f"{i}"
        w_i = width_in_pixels(FONT_XXS_SDK, _i)

        if (y + h) > H_PANEL:
            print(">>> new column")
            y = 0
            x += w_max_in_column
            w_max_in_column = w + w_i            
        else:
            w_max_in_column = max(w_max_in_column, w + w_i)
            
            
        y += h

        print(f"{i} Font: {name} h={h} y={y} w={w} x={x}")
        
        try:            
            graphics.DrawText(cnv, FONT_XXS_SDK, x, y, COLOR_7C_BLUE, _i)
            _x = x + w_i
            graphics.DrawText(cnv, font, _x, y, COLOR_7C_BLUE, "0")
        
        except TypeError as ex:
            print(f"\t -> \t{ex}")
        except AttributeError as ex:
            print(f"\t -> \t{ex}")
            