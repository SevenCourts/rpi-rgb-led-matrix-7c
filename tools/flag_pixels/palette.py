"""LED-friendly saturated palette for hand-authored flags.

The matrix renders subtle shades poorly, so we keep a small set of high-chroma
colors. Where a flag's official color is dull (e.g. UK navy), we bump
saturation slightly so it reads on the panel.
"""

# Core primaries
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
RED = (220, 0, 25)
DARK_RED = (160, 0, 20)
BLUE = (0, 60, 165)            # UK / Australia / NZ field
DARK_BLUE = (0, 30, 110)
LIGHT_BLUE = (90, 175, 230)    # Argentina, Fiji, Tuvalu field
YELLOW = (255, 220, 0)
GOLD = (235, 180, 30)          # Sri Lanka border, Mexico/Spain coat hints
ORANGE = (255, 125, 0)
GREEN = (0, 165, 70)           # Mexico, Portugal, Brazil
DARK_GREEN = (0, 110, 50)
MAROON = (130, 30, 50)         # Sri Lanka field
SAFFRON = (240, 145, 30)       # Sri Lanka panel

# Semantic aliases
UK_BLUE = BLUE
UK_RED = RED
BRAZIL_GREEN = (0, 145, 60)
BRAZIL_YELLOW = (255, 220, 0)
BRAZIL_BLUE = (0, 40, 120)
ARGENTINA_BLUE = LIGHT_BLUE
ARGENTINA_SUN = (240, 180, 30)
MEXICO_GREEN = (0, 130, 70)
MEXICO_RED = (200, 20, 40)
SPAIN_YELLOW = (250, 200, 0)
SPAIN_RED = (200, 10, 30)
PORTUGAL_GREEN = (0, 130, 70)
PORTUGAL_RED = (220, 30, 35)
