"""The free-court prompt must stay on the panel, descenders included.

"Book now via eBuSy" fitted into one row. "Book now via Playtomic" wrapped, and
its second row sat 2 rows above the panel edge while the font needs 3 below the
baseline, so the tail of the "y" was cut off on the M1 (led-df2).

The prompt now reads "Book on <provider>" and both fit into one row (led-dbn);
a longer provider name still wraps.

Run with: python -m unittest tests.test_booking_prompt
(or via pytest if installed)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("USE_RGB_MATRIX_EMULATOR", "1")
os.environ.setdefault("PANEL_TYPE", "M1")

from sevencourts import club_styles  # noqa: E402
from sevencourts.m1.booking import view_single  # noqa: E402
from sevencourts.m1.dimens import H_PANEL, W_PANEL  # noqa: E402
from sevencourts.m1.model import PanelState  # noqa: E402


class _Canvas:
    """Records every pixel a view sets, on the panel or past its edges."""

    width = W_PANEL
    height = H_PANEL

    def __init__(self):
        self.pixels = {}

    def SetPixel(self, x, y, r, g, b):
        self.pixels[(x, y)] = (r, g, b)

    def SetImage(self, image, x=0, y=0):
        pass


def _prompt_rows(style, provider):
    """Panel rows holding prompt-coloured pixels on a free single court."""
    booking = {
        "style": "any",
        "_dev_timestamp": "2026-05-25T14:30:00+02:00",
        "courts": [
            {
                "court": {"id": 1, "name": "Single", "shortName": "S"},
                "past": None,
                "current": None,
                "next": None,
            }
        ],
    }
    if provider:
        booking["provider"] = provider
    cnv = _Canvas()
    view_single.draw(cnv, PanelState(panel_info={"booking": booking}), style)
    c = style.booking.one.c_prompt
    prompt_color = (c.red, c.green, c.blue)
    return sorted({y for (_, y), rgb in cnv.pixels.items() if rgb == prompt_color})


class FreeCourtPromptTest(unittest.TestCase):
    # Court name on top, and court name on the left.
    styles = (club_styles.style_TABB, club_styles.style_SevenCourts)

    def test_two_row_prompt_keeps_its_descenders_on_the_panel(self):
        for style in self.styles:
            rows = _prompt_rows(style, "Playtomic Booking App")
            # 8 rows of "Book on Playtomic", 8 of "Booking App", 3 of the "g"
            # tail and the 2 rows between the lines.
            self.assertEqual((rows[0], rows[-1]), (H_PANEL - 21, H_PANEL - 1))

    def test_one_row_prompt_stays_where_it_was(self):
        for style in self.styles:
            # None: older backends send no provider and get eBuSy.
            for provider in (None, "Playtomic"):
                rows = _prompt_rows(style, provider)
                self.assertEqual((rows[0], rows[-1]), (H_PANEL - 12, H_PANEL - 2))


if __name__ == "__main__":
    unittest.main()
