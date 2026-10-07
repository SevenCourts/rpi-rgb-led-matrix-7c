from datetime import timedelta, datetime
from sevencourts.rgbmatrix import *
from sevencourts.m1.model import (
    PERIOD_INTERCHANGE_ADJACENT_S,
    is_current_second_in_period,
)

TD_1_WELCOME = timedelta(minutes=2)
TD_3_COUNTDOWN = TD_0_UPCOMING = timedelta(minutes=-5)  # these two should be equal
TD_4_GAMEOVER = timedelta(minutes=2)


def hours_minutes_diff(t1: datetime, t2: datetime) -> tuple[int, int, int]:
    seconds_left = (t1 - t2).seconds - 1
    minutes_in_hour_left = seconds_left // 60 % 60 + 1
    hours_left = seconds_left // (60 * 60)
    return (hours_left, minutes_in_hour_left)


def booking_info_texts(
    booking, w_max_px: int, fonts: tuple[graphics.Font]
) -> tuple[tuple[str], graphics.Font]:
    # FIXME should be given by extra Booking API? #is_display_p1_name
    no_person_name_booking_types = {"Training", "Verbandspiel"}  # , 'Mit Ballmaschine'}

    text = ""
    max_len = 0
    font = fonts[0]
    if booking:
        if booking.get("display-text"):
            text = booking.get("display-text")
        elif booking.get("booking-type", "") in no_person_name_booking_types and not (
            booking.get("p2") or booking.get("p3") or booking.get("p4")
        ):
            text = booking.get("booking-type")
        elif booking.get("p3") or booking.get("p4"):
            text = _booking_team(booking, True) + " " + _booking_team(booking, False)
        else:
            text = (
                _booking_player(booking.get("p1"))
                + " "
                + _booking_player(booking.get("p2"))
            )
        text = text.strip()

        max_len = max_string_length_for_font(font, w_max_px)
        if len(text) > max_len:
            font = fonts[1]
            max_len = max_string_length_for_font(font, w_max_px)

    return (truncate_text(text, max_len, ellipsize=True), font)


def _booking_player(player):
    txt = ""
    if player:
        firstname = player.get("firstname")

        if firstname:
            txt = firstname
        else:
            lastname = player.get("lastname")
            if lastname:
                txt = lastname
            else:
                txt = ""  # FIXME guests?
    return txt


def _booking_team(booking, isTeam1=True):
    txt = ""
    tp1 = booking.get("p1") if isTeam1 else booking.get("p3")
    if tp1:
        txt = _booking_player(tp1)
    tp2 = booking.get("p2") if isTeam1 else booking.get("p4")
    if tp2:
        if txt:
            txt += " "
        txt = (txt or "") + _booking_player(tp2)
    return txt


def weather_text(weather_info, s) -> str:
    """The temperature to show for style `s`, e.g. "21°", or "" for none.

    Only a reading fetched for this style's city counts: after a style switch
    the previous city's reading lingers until the next fetch.
    """
    if (
        weather_info
        and s.booking.is_weather_displayed
        and weather_info.get("city") == s.booking.weather_city
    ):
        return f"{weather_info.get('temperature')}°"
    return ""
