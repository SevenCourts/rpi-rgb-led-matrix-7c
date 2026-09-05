"""Regression tests for the image + clock split decision in view_image.

A pre-rendered "with clock" asset is exactly W_LOGO_WITH_CLOCK wide; it must
still leave room for the clock.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("USE_RGB_MATRIX_EMULATOR", "1")
os.environ.setdefault("IMAGES_CACHE_DIR", "/tmp/7c_test_imgs")
os.environ.setdefault("PANEL_TYPE", "M1")

from PIL import Image  # noqa: E402

from sevencourts.m1.dimens import H_PANEL, W_LOGO_WITH_CLOCK  # noqa: E402
from sevencourts.m1.view_image import _can_show_clock  # noqa: E402


class TestCanShowClock(unittest.TestCase):
    def test_exact_clock_width_shows_clock(self):
        self.assertTrue(_can_show_clock(Image.new("RGB", (W_LOGO_WITH_CLOCK, H_PANEL))))

    def test_narrower_shows_clock(self):
        self.assertTrue(_can_show_clock(Image.new("RGB", (W_LOGO_WITH_CLOCK - 1, H_PANEL))))

    def test_wider_hides_clock(self):
        self.assertFalse(_can_show_clock(Image.new("RGB", (W_LOGO_WITH_CLOCK + 1, H_PANEL))))


if __name__ == "__main__":
    unittest.main()
