"""Payload in, PNG out."""

from datetime import datetime
from typing import Optional, Tuple

from dateutil import tz

import sevencourts.logging as logging
import sevencourts.m1.view as view
from sevencourts.m1.dimens import H_PANEL, W_PANEL
from sevencourts.m1.model import (
    PERIOD_INTERCHANGE_ADJACENT_S,
    PanelState,
    is_current_second_in_period,
)
from sevencourts.render.canvas import RenderCanvas

_log = logging.logger("render")

# Width and height in pixels of the panel type this process draws.
PANEL_SIZE = (W_PANEL, H_PANEL)

# Any id will do: without one the views draw the "not registered yet" screen.
_PANEL_ID = "preview"


def render(
    panel_info: Optional[dict],
    now: datetime,
    *,
    weather: Optional[dict] = None,
    comm_error: bool = False,
) -> Tuple[bytes, Optional[str]]:
    """Draw what a panel shows for `panel_info` at the moment `now`.

    `panel_info` is the body of GET /panels/<id>/match. `now` must carry a
    time zone; the clock is shown in the panel's own zone. `weather` is a
    reading as openweathermap.fetch_weather returns it, or None for no
    weather. `comm_error` draws the "cannot reach the server" indicator.

    Returns the PNG at the panel's native resolution, and the error message
    when drawing failed and the PNG shows the panel's error screen instead.
    """
    if now.tzinfo is None:
        raise ValueError("now must carry a time zone")

    state = PanelState(
        panel_info=panel_info or {},
        weather_info=weather or {},
        panel_id=_PANEL_ID,
        server_communication_error=comm_error,
    )
    now_in_tz = now.astimezone(tz.gettz(state.tz()))
    state.panel_info = _with_booking_time(state.panel_info, now_in_tz)
    # As PanelState.refresh_time does on a panel, but from `now`.
    state.time_now_in_TZ = now_in_tz.strftime("%H:%M")
    state.is_next_booking_turn = (
        "booking" in state.panel_info
        and is_current_second_in_period(now_in_tz, PERIOD_INTERCHANGE_ADJACENT_S)
    )

    cnv = RenderCanvas(W_PANEL, H_PANEL)
    error = view.draw_safely(cnv, state)
    if error is not None:
        _log.error(f"❌ Error during drawing: {error}", exc_info=error)
    return cnv.png(), (None if error is None else str(error) or repr(error))


def _with_booking_time(panel_info: dict, now_in_tz: datetime) -> dict:
    """A booking payload that says itself what time it is.

    Without _dev_timestamp the booking views read the state's "HH:MM" as a
    time of the process's own today. That is the panel's today on a panel, but
    not here: the process may run in another time zone, and `now` may be any
    moment. So the moment is handed over in full.
    """
    booking = panel_info.get("booking")
    if not isinstance(booking, dict) or booking.get("_dev_timestamp"):
        return panel_info
    return {**panel_info, "booking": {**booking, "_dev_timestamp": now_in_tz.isoformat()}}
