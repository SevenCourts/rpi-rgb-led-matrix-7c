"""Sanity tests for the panel-type Layout system.

Validates that the M1 Layout has every required field populated and that
`current_layout()` raises a clear NotImplementedError for non-M1 panel types.
"""

import dataclasses
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("USE_RGB_MATRIX_EMULATOR", "1")
os.environ.setdefault("IMAGES_CACHE_DIR", "/tmp/7c_test_imgs")
os.environ.setdefault("PANEL_TYPE", "M1")


_OPTIONAL_FIELDS_ALLOWED_NONE = {
    # MessageLayout.clock_divider_y is optional: when None, no divider is drawn.
    # On M1 the clock overlaps the message zone — no divider, by design.
    ("message", "clock_divider_y"),
}


class TestM1Layout(unittest.TestCase):
    def test_m1_layout_has_no_none_fields(self):
        from sevencourts.m1.layouts import current_layout

        layout = current_layout()

        for view_field in dataclasses.fields(layout):
            view_layout = getattr(layout, view_field.name)
            for f in dataclasses.fields(view_layout):
                if (view_field.name, f.name) in _OPTIONAL_FIELDS_ALLOWED_NONE:
                    continue
                value = getattr(view_layout, f.name)
                self.assertIsNotNone(
                    value,
                    f"{view_field.name}.{f.name} must not be None on M1",
                )

    def test_scoreboard_geometry_matches_legacy_constants(self):
        from sevencourts.m1.layouts import current_layout

        sb = current_layout().scoreboard
        self.assertEqual(sb.x_score_game, 163)
        self.assertEqual(sb.x_score_service, 155)
        self.assertEqual(sb.w_score_set, 20)
        self.assertEqual(sb.margin_names_scoreboard, 3)
        self.assertTrue(sb.upper_case_names)

    def test_signage_name_lengths_match_legacy(self):
        from sevencourts.m1.layouts import current_layout

        sig = current_layout().signage
        self.assertEqual(sig.max_length_name_singles, 14)
        self.assertEqual(sig.max_length_name_doubles, 3)


class TestXL1Layout(unittest.TestCase):
    """XL1 Layout smoke test — runs in a subprocess to keep PANEL_TYPE=M1
    cached in the in-process module-level globals of other tests."""

    def test_xl1_layout_has_no_none_fields(self):
        import subprocess
        import sys

        code = (
            "import os, dataclasses;"
            "os.environ['PANEL_TYPE']='XL1';"
            "os.environ.setdefault('USE_RGB_MATRIX_EMULATOR','1');"
            "os.environ.setdefault('IMAGES_CACHE_DIR','/tmp/7c_test_imgs');"
            "from sevencourts.m1.layouts import current_layout;"
            "layout = current_layout();"
            "exceptions = {('message','clock_x'),('message','clock_divider_y')};"
            "missing=[];"
            "[missing.append(f'{v.name}.{f.name}')"
            " for v in dataclasses.fields(layout)"
            " for f in dataclasses.fields(getattr(layout, v.name))"
            " if (v.name,f.name) not in exceptions"
            " and getattr(getattr(layout, v.name), f.name) is None];"
            "assert not missing, missing;"
            "sb=layout.scoreboard;"
            "assert sb.x_min_scoreboard==204, sb.x_min_scoreboard;"
            # FONT_L_7SEGMENT (17-px advance): 2-digit width 34 px right-aligns
            # to x=316 (right margin 4 px from panel edge) → starts at x=282.
            "assert sb.x_score_game==282;"
            # Half-advance shift centers single-char scores ("A") in the slot.
            "assert sb.dx_score_game_single_digit==9;"
            "assert sb.w_score_set==22;"
            "sig=layout.signage;"
            "assert sig.max_length_name_singles==12;"
            "assert sig.max_length_name_doubles==5;"
            "msg=layout.message;"
            "assert msg.clock_divider_y is None;"  # divider removed after bench review
            "assert msg.clock_right_aligned is True;"
            "print('ok')"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        self.assertEqual(
            result.returncode, 0, msg=f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
        )
        self.assertIn("ok", result.stdout)


class TestPickFontThatFitsBackwardCompat(unittest.TestCase):
    def test_default_candidates_match_legacy_behaviour(self):
        from sevencourts.rgbmatrix import (
            FONT_L,
            FONT_M,
            FONT_S,
            pick_font_that_fits,
        )

        for w, h, text in [
            (200, 30, "ABC"),
            (50, 30, "ABC"),
            (10, 5, "ABC"),
            (200, 30, "VERY LONG TEXT THAT WILL NOT FIT FONT_L EASILY"),
        ]:
            self.assertIs(
                pick_font_that_fits(w, h, text),
                pick_font_that_fits(w, h, text, candidates=[FONT_L, FONT_M, FONT_S]),
                f"Default and explicit candidates must agree for ({w},{h},{text!r})",
            )


if __name__ == "__main__":
    unittest.main()
