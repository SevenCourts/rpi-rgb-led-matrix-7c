"""The headless renderer: a panel payload in, a PNG out (led-6c2).

sevencourts.render draws with the views of the firmware on a PIL-backed
canvas, for the panel preview of the tableau server (hub-0a0p). Three things
are checked here:

- golden PNGs for M1, L1 and XL1, one subprocess per type because PANEL_TYPE
  is frozen at import (tests/render_goldens.py holds the scenarios);
- that the canvas gives the same pixels as RGBMatrixEmulator's own canvas,
  which is what tools/emulators/emulators.sh shows;
- that the time comes from the `now` argument and from nothing else.

Run with: python -m unittest tests.test_render
(or via pytest if installed)
"""

import os
import sys
import unittest
import unittest.mock
from datetime import datetime, timedelta
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("USE_RGB_MATRIX_EMULATOR", "1")
os.environ.setdefault("PANEL_TYPE", "M1")
os.environ.setdefault("IMAGES_CACHE_DIR", "/tmp/7c_test_imgs")

from PIL import Image  # noqa: E402

from sevencourts.m1.dimens import H_PANEL, W_PANEL  # noqa: E402
from sevencourts.render import PANEL_SIZE, RenderCanvas, core, render  # noqa: E402
from tests import render_goldens  # noqa: E402

NOW = datetime.fromisoformat("2026-05-25T14:30:00+02:00")

CLOCK = {"idle-info": {"timezone": "Europe/Berlin", "clock": True}}


def _pixels(png: bytes) -> Image.Image:
    return Image.open(BytesIO(png)).convert("RGB")


def _same(a: bytes, b: bytes) -> bool:
    return _pixels(a).tobytes() == _pixels(b).tobytes()


def _slot(start: datetime, end: datetime, name: str) -> dict:
    return {
        "start-date": start.isoformat(),
        "end-date": end.isoformat(),
        "p1": {"firstname": name},
    }


def _booking(at: datetime) -> dict:
    """A court whose booking ends 3 minutes after `at`, with another to follow."""
    end = (at + timedelta(minutes=3)).replace(second=0)
    return {
        "booking": {
            "style": "SevenCourts",
            "courts": [
                {
                    "court": {"id": 1, "name": "Court 1", "shortName": "C1"},
                    "past": None,
                    "current": _slot(end - timedelta(hours=1), end, "Anna"),
                    "next": _slot(end, end + timedelta(hours=1), "Boris"),
                }
            ],
        }
    }


class GoldenTest(unittest.TestCase):
    """What each screen looks like, per panel type."""

    def _check(self, panel_type):
        result = render_goldens.run_type_in_subprocess(panel_type)
        self.assertEqual(
            result.returncode, 0, msg=f"\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        self.assertIn("goldens match", result.stdout)

    def test_m1(self):
        self._check("M1")

    def test_l1(self):
        self._check("L1")

    def test_xl1(self):
        self._check("XL1")


class RenderCanvasTest(unittest.TestCase):
    def test_starts_black_at_the_given_size(self):
        image = RenderCanvas(5, 3).image()
        self.assertEqual(image.size, (5, 3))
        self.assertEqual(image.getcolors(), [(15, (0, 0, 0))])

    def test_set_pixel(self):
        cnv = RenderCanvas(5, 3)
        cnv.SetPixel(4, 2, 10, 20, 30)
        self.assertEqual(cnv.image().getpixel((4, 2)), (10, 20, 30))

    def test_set_pixel_takes_the_floats_the_views_pass(self):
        cnv = RenderCanvas(5, 3)
        cnv.SetPixel(1.0, 2.0, 255, 0, 0)
        self.assertEqual(cnv.image().getpixel((1, 2)), (255, 0, 0))

    def test_set_pixel_outside_the_canvas_is_ignored(self):
        cnv = RenderCanvas(5, 3)
        for x, y in ((-1, 0), (0, -1), (5, 0), (0, 3), (99, 99)):
            cnv.SetPixel(x, y, 255, 255, 255)
        self.assertEqual(cnv.image().getcolors(), [(15, (0, 0, 0))])

    def test_set_image_pastes_at_the_offset_and_clips(self):
        cnv = RenderCanvas(5, 3)
        cnv.SetImage(Image.new("RGB", (4, 4), (1, 2, 3)), 3, 1)
        image = cnv.image()
        self.assertEqual(image.getpixel((2, 1)), (0, 0, 0))
        self.assertEqual(image.getpixel((3, 1)), (1, 2, 3))
        self.assertEqual(image.getpixel((4, 2)), (1, 2, 3))

    def test_clear(self):
        cnv = RenderCanvas(5, 3)
        cnv.SetPixel(0, 0, 255, 255, 255)
        cnv.Clear()
        self.assertEqual(cnv.image().getcolors(), [(15, (0, 0, 0))])

    def test_png_is_the_native_resolution(self):
        self.assertEqual(_pixels(RenderCanvas(5, 3).png()).size, (5, 3))


class _EmulatorOptions:
    """As much of RGBMatrixOptions as RGBMatrixEmulator's Canvas reads."""

    cols, rows = W_PANEL, H_PANEL
    chain_length = parallel = 1
    brightness = 100

    class display_adapter:
        @staticmethod
        def get_instance(width, height, options):
            return _EmulatorOptions.display_adapter()

        def load_emulator_window(self):
            pass


class SameAsEmulatorTest(unittest.TestCase):
    """The PNG holds the pixels the emulator's canvas would hold."""

    def _on_emulator_canvas(self, panel_info, **kwargs) -> bytes:
        from RGBMatrixEmulator.emulation.canvas import Canvas

        class _EmulatorCanvas(Canvas):
            def __init__(self, width, height):
                super().__init__(_EmulatorOptions())

            def png(self):
                out = BytesIO()
                Image.fromarray(self._Canvas__pixels, "RGB").save(out, format="PNG")
                return out.getvalue()

        with unittest.mock.patch.object(core, "RenderCanvas", _EmulatorCanvas):
            return render(panel_info, NOW, **kwargs)[0]

    def test_scenarios_without_a_download(self):
        compared = 0
        for name, panel_info, now, kwargs in render_goldens.scenarios("http://unused"):
            if now != render_goldens.NOW or "image-url" in str(panel_info) or "ads" in name:
                continue
            with self.subTest(scenario=name):
                self.assertTrue(
                    _same(
                        render(panel_info, NOW, **kwargs)[0],
                        self._on_emulator_canvas(panel_info, **kwargs),
                    )
                )
            compared += 1
        self.assertGreater(compared, 12)


class RenderTest(unittest.TestCase):
    def test_returns_a_png_of_the_panel_size_and_no_error(self):
        png, error = render(CLOCK, NOW)
        self.assertIsNone(error)
        self.assertEqual(_pixels(png).size, (W_PANEL, H_PANEL))
        self.assertEqual(PANEL_SIZE, (W_PANEL, H_PANEL))

    def test_now_without_a_time_zone_is_refused(self):
        with self.assertRaises(ValueError):
            render(CLOCK, datetime(2026, 5, 25, 14, 30))

    def test_none_and_empty_info_draw_the_same_screen(self):
        self.assertTrue(_same(render(None, NOW)[0], render({}, NOW)[0]))

    def test_the_minute_shows(self):
        self.assertFalse(
            _same(render(CLOCK, NOW)[0], render(CLOCK, NOW + timedelta(minutes=1))[0])
        )

    def test_seconds_do_not_show_outside_booking(self):
        self.assertTrue(
            _same(render(CLOCK, NOW)[0], render(CLOCK, NOW + timedelta(seconds=59))[0])
        )

    def test_the_clock_is_in_the_time_zone_of_the_panel(self):
        tokyo = {"idle-info": {"timezone": "Asia/Tokyo", "clock": True}}
        # 14:30 in Berlin (UTC+2) is 21:30 in Tokyo (UTC+9).
        self.assertFalse(_same(render(tokyo, NOW)[0], render(CLOCK, NOW)[0]))
        self.assertTrue(
            _same(render(tokyo, NOW)[0], render(CLOCK, NOW + timedelta(hours=7))[0])
        )

    def test_the_time_zone_of_now_does_not_matter(self):
        from dateutil import tz

        self.assertTrue(
            _same(render(CLOCK, NOW)[0], render(CLOCK, NOW.astimezone(tz.UTC))[0])
        )

    def test_server_communication_error_shows(self):
        self.assertFalse(
            _same(render(CLOCK, NOW)[0], render(CLOCK, NOW, comm_error=True)[0])
        )

    def test_a_failing_view_gives_the_error_screen_and_the_message(self):
        png, error = render({"signage-info": None}, NOW)
        self.assertIn("NoneType", error)
        self.assertEqual(_pixels(png).size, (W_PANEL, H_PANEL))
        self.assertFalse(_same(png, render({}, NOW)[0]))


class BookingTimeTest(unittest.TestCase):
    """The booking views must take the moment from `now`, in full.

    Left alone they read the state's "HH:MM" as a time of the process's own
    today: wrong for any other day, and around midnight when the process and
    the panel are in different time zones.
    """

    def _stamped(self, info, at):
        return {"booking": {**info["booking"], "_dev_timestamp": at.isoformat()}}

    def test_another_day_than_today(self):
        for at in (
            datetime.fromisoformat("2030-01-15T10:57:00+01:00"),
            # The booking ends at midnight; in UTC it is still the day before.
            datetime.fromisoformat("2030-07-01T23:57:00+02:00"),
            datetime.fromisoformat("2030-07-02T00:27:00+02:00"),
        ):
            with self.subTest(at=at.isoformat()):
                info = _booking(at)
                png, error = render(info, at)
                self.assertIsNone(error)
                self.assertTrue(_same(png, render(self._stamped(info, at), at)[0]))
                # ... and that is not what any other minute looks like.
                self.assertFalse(_same(png, render(info, at + timedelta(minutes=1))[0]))

    def test_current_and_next_booking_take_turns_every_10_seconds(self):
        at = datetime.fromisoformat("2030-01-15T10:57:00+01:00")
        info = _booking(at)
        current = render(info, at + timedelta(seconds=10))[0]
        upcoming = render(info, at)[0]
        self.assertFalse(_same(current, upcoming))
        self.assertTrue(_same(current, render(info, at + timedelta(seconds=19))[0]))
        self.assertTrue(_same(upcoming, render(info, at + timedelta(seconds=20))[0]))

    def test_a_timestamp_set_in_the_panel_admin_wins(self):
        at = datetime.fromisoformat("2030-01-15T10:57:00+01:00")
        info = self._stamped(_booking(at), at)
        self.assertTrue(
            _same(render(info, at)[0], render(info, at + timedelta(hours=5))[0])
        )

    def test_the_payload_is_left_as_it_was(self):
        at = datetime.fromisoformat("2030-01-15T10:57:00+01:00")
        info = _booking(at)
        render(info, at)
        self.assertNotIn("_dev_timestamp", info["booking"])


if __name__ == "__main__":
    unittest.main()
