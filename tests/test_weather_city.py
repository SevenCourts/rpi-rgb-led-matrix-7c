"""The weather row shows the temperature of the selected booking style's city.

The city used to be hardcoded to Böblingen for every panel, and fetch_weather
ignored its `city` argument. A club in another town (Padel Club Esslingen) must
get its own weather, and a reading fetched for one city must never be drawn
under another club's style.
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("USE_RGB_MATRIX_EMULATOR", "1")
os.environ.setdefault("IMAGES_CACHE_DIR", "/tmp/7c_test_imgs")
os.environ.setdefault("PANEL_TYPE", "M1")

ESSLINGEN = "Esslingen am Neckar,DE"
BOEBLINGEN = "Böblingen,DE"


def _booking(style):
    return {"booking": {"style": style, "courts": []}}


class TestStyleWeatherCity(unittest.TestCase):
    def _city(self, panel_info):
        from sevencourts.club_styles import style_for

        return style_for(panel_info).booking.weather_city

    def test_padel_club_esslingen_gets_esslingen(self):
        self.assertEqual(self._city(_booking("Padel Club Esslingen")), ESSLINGEN)

    def test_tabb_keeps_boeblingen(self):
        self.assertEqual(self._city(_booking("TABB")), BOEBLINGEN)

    def test_unknown_style_and_missing_info_fall_back(self):
        from sevencourts.club_styles import style_for, style_SevenCourts

        for info in (_booking("No Such Club"), {}, None, {"booking": None}):
            self.assertIs(style_for(info), style_SevenCourts)

    def test_every_weather_style_names_a_city(self):
        from sevencourts.club_styles import STYLES

        for name, style in STYLES.items():
            if style.booking.is_weather_displayed:
                self.assertTrue(style.booking.weather_city, name)


class TestFetchWeatherUsesCity(unittest.TestCase):
    def test_request_asks_for_the_given_city(self):
        import sevencourts.openweathermap as owm

        response = mock.Mock(status_code=200)
        response.json.return_value = {"main": {"temp": 17.6, "humidity": 60}}
        with mock.patch.object(owm.requests, "get", return_value=response) as get:
            info = owm.fetch_weather(city=ESSLINGEN)

        self.assertEqual(get.call_args.kwargs["params"]["q"], ESSLINGEN)
        self.assertEqual(info["city"], ESSLINGEN)
        self.assertEqual(info["temperature"], 17)


class TestWeatherRowMatchesCity(unittest.TestCase):
    def _drawn_texts(self, weather_info):
        import sevencourts.m1.booking.view_multiple as vm
        from sevencourts.club_styles import style_PadelClubEsslingen

        with mock.patch.object(vm.graphics, "DrawText") as draw_text:
            vm._draw_club_area(
                mock.MagicMock(), weather_info, 126, 0, 66, style_PadelClubEsslingen
            )
        return [c.args[-1] for c in draw_text.call_args_list]

    def test_own_city_is_drawn(self):
        texts = self._drawn_texts({"city": ESSLINGEN, "temperature": 17})
        self.assertEqual(texts, [" 17°"])

    def test_other_city_is_not_drawn(self):
        texts = self._drawn_texts({"city": BOEBLINGEN, "temperature": 14})
        self.assertEqual(texts, [])


class TestSingleCourtHeaderWeather(unittest.TestCase):
    """Single-court view: the temperature sits in the court-name header."""

    def _header_texts(self, style_name, weather_info):
        import sevencourts.m1.booking.view_single as vs
        from sevencourts.m1.model import PanelState

        state = PanelState()
        state.panel_info = {
            "booking": {
                "style": style_name,
                "_dev_timestamp": "2026-05-25T14:30:00+02:00",
                "courts": [
                    {
                        "court": {"id": 1, "name": "Court 1", "shortName": "C1"},
                        "past": None,
                        "current": None,
                        "next": None,
                    }
                ],
            }
        }
        state.weather_info = weather_info
        from sevencourts.club_styles import style_for

        with mock.patch.object(vs, "draw_text") as draw_text:
            vs.draw(mock.MagicMock(), state, style_for(state.panel_info))
        return [c.args[3] for c in draw_text.call_args_list]

    def test_esslingen_reading_is_in_the_header(self):
        texts = self._header_texts(
            "Padel Club Esslingen", {"city": ESSLINGEN, "temperature": 17}
        )
        self.assertIn("17°", texts)
        self.assertIn("Court 1", texts)

    def test_boeblingen_reading_is_not_shown_for_esslingen(self):
        texts = self._header_texts(
            "Padel Club Esslingen", {"city": BOEBLINGEN, "temperature": 14}
        )
        self.assertNotIn("14°", texts)

    def test_no_weather_info_draws_no_temperature(self):
        for info in (None, {}):
            texts = self._header_texts("Padel Club Esslingen", info)
            self.assertFalse([t for t in texts if "°" in t])

    def test_other_styles_single_court_view_is_unchanged(self):
        texts = self._header_texts("TABB", {"city": BOEBLINGEN, "temperature": 14})
        self.assertNotIn("14°", texts)


if __name__ == "__main__":
    unittest.main()
