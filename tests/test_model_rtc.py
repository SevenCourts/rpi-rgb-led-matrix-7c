"""Unit tests for RTC detection in sevencourts.m1.model.

Run with: python -m unittest tests.test_model_rtc
(or via pytest if installed)
"""
import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sevencourts.m1 import model  # noqa: E402


class IsRtcTickingTest(unittest.TestCase):
    def setUp(self):
        # Default: NTP NOT synced unless a test overrides — isolates the
        # year-sanity branch from the delta-vs-sysclock branch.
        self.ntp_patch = patch.object(model, "_is_ntp_synchronized", return_value=False)
        self.ntp_patch.start()
        self.addCleanup(self.ntp_patch.stop)

    def _with_rtc(self, dt_or_exc):
        if isinstance(dt_or_exc, Exception):
            return patch.object(model, "_read_rtc_time", side_effect=dt_or_exc)
        return patch.object(model, "_read_rtc_time", return_value=dt_or_exc)

    def test_healthy_rtc_returns_true(self):
        with self._with_rtc(datetime(2026, 5, 23, 18, 9, 34)):
            self.assertTrue(model._is_rtc_ticking())

    def test_rtc_at_1970_returns_false(self):
        with self._with_rtc(datetime(1970, 1, 1, 0, 0, 0)):
            self.assertFalse(model._is_rtc_ticking())

    def test_rtc_at_2044_when_ntp_synced_returns_false(self):
        # Corrupted-chip scenario: RTC reads 2044, NTP has corrected sysclock to 2026.
        self.ntp_patch.stop()
        with patch.object(model, "_is_ntp_synchronized", return_value=True), \
             self._with_rtc(datetime(2044, 1, 1, 0, 0, 0)):
            self.assertFalse(model._is_rtc_ticking())

    def test_rtc_above_year_2100_returns_false(self):
        # Even without NTP, an absurd year fails the sanity bound.
        with self._with_rtc(datetime(2100, 1, 1, 0, 0, 0)):
            self.assertFalse(model._is_rtc_ticking())

    def test_hwclock_read_fails_returns_false(self):
        with self._with_rtc(OSError("Invalid argument")):
            self.assertFalse(model._is_rtc_ticking())

    def test_dev_rtc_missing_returns_false(self):
        with self._with_rtc(FileNotFoundError("/dev/rtc0")):
            self.assertFalse(model._is_rtc_ticking())

    def test_ntp_synced_and_rtc_agrees_within_tolerance(self):
        self.ntp_patch.stop()
        now = datetime.utcnow()
        with patch.object(model, "_is_ntp_synchronized", return_value=True), \
             self._with_rtc(now + timedelta(seconds=30)):
            self.assertTrue(model._is_rtc_ticking())

    def test_ntp_synced_but_rtc_far_off_returns_false(self):
        self.ntp_patch.stop()
        now = datetime.utcnow()
        with patch.object(model, "_is_ntp_synchronized", return_value=True), \
             self._with_rtc(now + timedelta(hours=1)):
            self.assertFalse(model._is_rtc_ticking())


if __name__ == "__main__":
    unittest.main()
