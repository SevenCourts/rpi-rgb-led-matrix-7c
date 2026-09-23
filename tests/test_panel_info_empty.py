"""The clock must keep ticking when the server sends no usable panel info.

On 2026-09-22 two new panels at Padel Club Esslingen got a falsy body on their
first /match poll. fetch_panel_info turned it into None, PanelState.tz() then
raised AttributeError in the once-a-second clock thread, the thread died, and
the displayed time froze until the app restarted (led-g4q).

Run with: python -m unittest tests.test_panel_info_empty
(or via pytest if installed)
"""

import io
import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sevencourts import gateway  # noqa: E402
from sevencourts.m1 import model  # noqa: E402


class _Response(io.BytesIO):
    def __init__(self, status, body: bytes):
        super().__init__(body)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FetchPanelInfoTest(unittest.TestCase):
    def setUp(self):
        for name, value in (("uptime", 1), ("cpu_temperature", 40)):
            p = patch.object(gateway.sys, name, return_value=value)
            p.start()
            self.addCleanup(p.stop)

    def _fetch(self, status, body: bytes):
        with patch.object(
            gateway.urllib.request, "urlopen", return_value=_Response(status, body)
        ):
            return gateway.fetch_panel_info("6d78175b")

    def test_match_over_false_is_an_empty_dict(self):
        self.assertEqual(self._fetch(200, b"false"), {})

    def test_null_and_empty_object_are_an_empty_dict(self):
        self.assertEqual(self._fetch(200, b"null"), {})
        self.assertEqual(self._fetch(200, b"{}"), {})

    def test_205_with_empty_body_is_an_empty_dict(self):
        self.assertEqual(self._fetch(205, b""), {})

    def test_other_status_is_an_empty_dict(self):
        self.assertEqual(self._fetch(204, b""), {})

    def test_non_object_json_is_an_empty_dict(self):
        self.assertEqual(self._fetch(200, b"[1, 2]"), {})

    def test_idle_info_passes_through(self):
        body = {"idle-info": {"clock": True, "timezone": "Europe/Zurich"}}
        self.assertEqual(self._fetch(205, json.dumps(body).encode()), body)


class TimezoneTest(unittest.TestCase):
    def test_none_panel_info_uses_default(self):
        self.assertEqual(model.PanelState(panel_info=None).tz(), model.DEFAULT_TIMEZONE)

    def test_null_idle_info_and_timezone_use_default(self):
        for info in ({"idle-info": None}, {"idle-info": {"timezone": None}}, {}):
            with self.subTest(info=info):
                self.assertEqual(model.PanelState(panel_info=info).tz(), model.DEFAULT_TIMEZONE)

    def test_configured_timezone_wins(self):
        info = {"idle-info": {"timezone": "Africa/Asmara"}}
        self.assertEqual(model.PanelState(panel_info=info).tz(), "Africa/Asmara")

    def test_refresh_time_with_none_panel_info_gives_a_time(self):
        with patch.object(model, "is_clock_trustworthy", return_value=True):
            now = model.PanelState(panel_info=None).refresh_time()
        self.assertRegex(now, r"^\d\d:\d\d$")


if __name__ == "__main__":
    unittest.main()
