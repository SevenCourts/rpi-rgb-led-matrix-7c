"""Unit tests for state-change logging in sevencourts.m1.model (led-ys3).

Run with: python -m unittest tests.test_model_state_log
(or via pytest if installed)
"""
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sevencourts.m1 import model  # noqa: E402


def _state(**kwargs):
    s = model.PanelState()
    for k, v in kwargs.items():
        setattr(s, k, v)
    return s


class ChangedFieldsTest(unittest.TestCase):
    def test_none_old_means_everything_changed(self):
        self.assertIn("panel_info", model.changed_fields(None, _state()))

    def test_clock_tick_is_the_only_change(self):
        old = _state(time_now_in_TZ="10:00")
        new = _state(time_now_in_TZ="10:01")
        self.assertEqual(["time_now_in_TZ"], model.changed_fields(old, new))

    def test_unchanged_state_reports_nothing(self):
        self.assertEqual([], model.changed_fields(_state(), _state()))

    def test_compare_false_fields_are_ignored(self):
        # last_updated_UTC is compare=False, so it must not count as a change:
        # it is refreshed on every poll and would defeat the whole check.
        old = _state(last_updated_UTC=datetime(2026, 1, 1))
        new = _state(last_updated_UTC=datetime(2026, 6, 1))
        self.assertEqual([], model.changed_fields(old, new))

    def test_real_change_is_named(self):
        old = _state(panel_id="p1")
        new = _state(panel_id="p2", server_communication_error=True)
        self.assertEqual(
            ["panel_id", "server_communication_error"],
            model.changed_fields(old, new),
        )


class StateChangeLogTest(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        self.log = model.StateChangeLog(full_interval_s=3600, clock=lambda: self.now)

    def test_first_transition_logs_the_full_state(self):
        lines = self.log.lines(None, _state(panel_id="p1"))
        self.assertEqual(["info", "info"], [lvl for lvl, _ in lines])
        self.assertIn("PanelState", lines[1][1])

    def test_clock_tick_is_debug_only(self):
        self.log.lines(None, _state(time_now_in_TZ="10:00"))  # consume heartbeat
        lines = self.log.lines(_state(time_now_in_TZ="10:00"), _state(time_now_in_TZ="10:01"))
        self.assertEqual([("debug", "🕑 Clock now 10:01, redrawing")], lines)

    def test_real_change_names_the_fields_without_the_full_repr(self):
        self.log.lines(None, _state())  # consume heartbeat
        lines = self.log.lines(_state(), _state(panel_id="p9"))
        self.assertEqual(1, len(lines))
        level, message = lines[0]
        self.assertEqual("info", level)
        self.assertIn("panel_id", message)
        self.assertNotIn("PanelState", message)

    def test_full_state_returns_on_the_heartbeat(self):
        self.log.lines(None, _state(time_now_in_TZ="10:00"))
        self.now = 3599
        lines = self.log.lines(_state(time_now_in_TZ="10:00"), _state(time_now_in_TZ="10:59"))
        self.assertEqual(1, len(lines))
        self.now = 3601
        lines = self.log.lines(_state(time_now_in_TZ="10:59"), _state(time_now_in_TZ="11:00"))
        self.assertEqual(2, len(lines))
        self.assertIn("PanelState", lines[1][1])

    def test_no_change_says_nothing(self):
        self.assertEqual([], self.log.lines(_state(), _state()))


class IdlePanelLogVolumeTest(unittest.TestCase):
    """The bead's acceptance criterion, as a test.

    A panel idle for 24h must add well under 1 MB to /tmp/sevencourts.log,
    which is tmpfs — i.e. RAM. Idle still means 1440 clock ticks.
    """

    def test_24h_idle_stays_far_under_1mb(self):
        now = [0.0]
        log = model.StateChangeLog(full_interval_s=3600, clock=lambda: now[0])
        previous = None
        info_bytes = 0
        for minute in range(1440):
            now[0] = minute * 60
            state = _state(time_now_in_TZ="%02d:%02d" % (minute // 60 % 24, minute % 60))
            for level, message in log.lines(previous, state):
                if level == "info":
                    info_bytes += len(message.encode()) + 60  # + timestamp/prefix
            previous = state

        self.assertLess(info_bytes, 100 * 1024, f"{info_bytes} bytes in 24h idle")

        # And for contrast, what the old code wrote: the full repr per change.
        old_bytes = 1440 * (len(repr(_state(time_now_in_TZ="10:00"))) + 60)
        self.assertGreater(old_bytes, 10 * info_bytes)


if __name__ == "__main__":
    unittest.main()
