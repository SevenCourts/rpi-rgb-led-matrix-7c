"""Adjacent bookings: current and next take turns in the last 5 minutes.

The booking views swap between the current booking (with the minutes left) and
the next one every 10 seconds. That stopped when the views began to take the
time from PanelState.time_now_in_TZ, which is "HH:MM": the second was always 0,
so it was always the next booking's turn, and the render loop redrew only once
a minute anyway (led-pbx).

The state now carries the turn itself, as a field that flips every 10 seconds.

Run with: python -m unittest tests.test_booking_interchange
(or via pytest if installed)
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime
from unittest import mock

from dateutil import tz

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("USE_RGB_MATRIX_EMULATOR", "1")
os.environ.setdefault("PANEL_TYPE", "M1")
os.environ.setdefault("IMAGES_CACHE_DIR", "/tmp/7c_test_imgs")

from sevencourts import club_styles  # noqa: E402
from sevencourts.m1 import model  # noqa: E402
from sevencourts.m1.booking import view_multiple, view_single  # noqa: E402
from sevencourts.m1.dimens import H_PANEL, W_PANEL  # noqa: E402
from sevencourts.m1.model import PanelState  # noqa: E402

TZ = "Europe/Berlin"


class _Canvas:
    """Records every pixel a view sets."""

    width = W_PANEL
    height = H_PANEL

    def __init__(self):
        self.pixels = {}

    def SetPixel(self, x, y, r, g, b):
        self.pixels[(x, y)] = (r, g, b)

    def SetImage(self, image, x=0, y=0):
        pass


def _today_at(hour):
    # The views read the state's "HH:MM" as a time of today.
    today = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
    return today.replace(tzinfo=tz.gettz(TZ)).isoformat()


def _slot(start, end, name):
    return {
        "start-date": _today_at(start),
        "end-date": _today_at(end),
        "p1": {"firstname": name},
    }


def _court(i):
    """A booking that ends at 15:00 and is directly followed by another."""
    return {
        "court": {"id": i, "name": f"Court {i}", "shortName": f"C{i}"},
        "past": None,
        "current": _slot(14, 15, "Anna"),
        "next": _slot(15, 16, "Boris"),
    }


def _state(courts, is_next_booking_turn):
    """A live panel at 14:57: no _dev_timestamp, the time comes from the state."""
    booking = {"style": "any", "courts": [_court(i + 1) for i in range(courts)]}
    return PanelState(
        panel_info={"booking": booking, "idle-info": {"timezone": TZ}},
        time_now_in_TZ="14:57",
        is_next_booking_turn=is_next_booking_turn,
    )


def _frozen_now(second):
    """datetime.now() in the model at 14:57:<second>."""

    class _Datetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 5, 25, 14, 57, second, tzinfo=tz)

    return mock.patch.object(model, "datetime", _Datetime)


def _draw(view, courts, is_next_booking_turn):
    """The texts the view put on the panel, in drawing order."""
    texts = []

    def record(cnv, font, x, y, color, text):
        texts.append(text)

    with mock.patch.object(view.graphics, "DrawText", record):
        view.draw(
            _Canvas(), _state(courts, is_next_booking_turn), club_styles.style_TABB
        )
    return [t for t in texts if t]


class TurnInTheStateTest(unittest.TestCase):
    def _refreshed(self, second, panel_info):
        state = PanelState(panel_info=panel_info)
        with _frozen_now(second), mock.patch.object(
            model, "is_clock_trustworthy", return_value=True
        ):
            state.refresh_time()
        return state

    def test_turn_flips_every_10_seconds_in_booking_mode(self):
        turns = [
            self._refreshed(s, {"booking": {}}).is_next_booking_turn
            for s in (0, 9, 10, 19, 20, 29, 30, 39, 40, 49, 50, 59)
        ]
        self.assertEqual([True, True, False, False] * 3, turns)

    def test_the_clock_itself_still_has_no_seconds(self):
        self.assertEqual("14:57", self._refreshed(42, {"booking": {}}).time_now_in_TZ)

    def test_no_turns_outside_booking_mode(self):
        # Otherwise a scoreboard or a clock would be redrawn every 10 seconds
        # for nothing.
        for panel_info in ({"team1": {}}, {"idle-info": {}}, {}, None):
            for second in (0, 10):
                self.assertFalse(
                    self._refreshed(second, panel_info).is_next_booking_turn
                )

    def test_a_flip_is_a_state_change_so_the_loop_redraws(self):
        self.assertNotEqual(_state(1, True), _state(1, False))

    def test_a_flip_is_not_written_to_the_state_file(self):
        # The state file is on the SD card: a write every 10 seconds would
        # wear it out.
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "state.json")
            with mock.patch.object(model, "PANEL_STATE_FILE", path), mock.patch.object(
                model, "_last_written_bytes", None
            ):
                model.write_to_file(_state(1, True))
                with open(path, "rb") as f:
                    written = f.read()
                self.assertNotIn(b"is_next_booking_turn", written)
                os.remove(path)
                model.write_to_file(_state(1, False))
                self.assertFalse(os.path.exists(path))
            # and a state file from before the field existed still loads
            with open(path, "wb") as f:
                f.write(written)
            with mock.patch.object(model, "PANEL_STATE_FILE", path):
                self.assertEqual("14:57", model.read_from_file().time_now_in_TZ)

    def test_a_flip_is_not_news_for_the_log(self):
        # The log lives in RAM on a panel (led-ys3).
        log = model.StateChangeLog(full_interval_s=3600, clock=lambda: 0.0)
        log.lines(None, _state(1, True))  # consume heartbeat
        lines = log.lines(_state(1, True), _state(1, False))
        self.assertEqual(["debug"], [lvl for lvl, _ in lines])


class SingleCourtTest(unittest.TestCase):
    def test_next_booking_on_its_turn(self):
        texts = _draw(view_single, 1, True)
        self.assertIn("Boris", texts)
        self.assertIn("Next booking", texts)
        self.assertIn("15:00", texts)
        self.assertIn("16:00", texts)
        self.assertNotIn("Anna", texts)

    def test_current_booking_on_its_turn(self):
        texts = _draw(view_single, 1, False)
        self.assertIn("Anna", texts)
        self.assertIn(" 3'", texts)
        self.assertNotIn("Boris", texts)
        self.assertNotIn("Next booking", texts)


class MultipleCourtsTest(unittest.TestCase):
    def test_next_bookings_on_their_turn(self):
        texts = _draw(view_multiple, 3, True)
        self.assertEqual(3, texts.count("Boris"))
        self.assertEqual(3, texts.count("15:00"))
        self.assertNotIn("Anna", texts)

    def test_current_bookings_on_their_turn(self):
        texts = _draw(view_multiple, 3, False)
        self.assertEqual(3, texts.count("Anna"))
        self.assertEqual(3, texts.count("3'"))
        self.assertNotIn("Boris", texts)


if __name__ == "__main__":
    unittest.main()
