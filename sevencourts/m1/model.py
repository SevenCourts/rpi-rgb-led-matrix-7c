from dataclasses import dataclass, field
from typing import Dict
from datetime import datetime
from dateutil import tz
import orjson
import os
import sevencourts.logging as logging

_log = logging.logger("model")

DEFAULT_TIMEZONE = "Europe/Berlin"

PANEL_STATE_FILE = os.getenv("PANEL_STATE_FILE", "last_state_from_server.json")


@dataclass
class PanelState:
    """
    Global infoboard state
    """

    panel_info: Dict = field(default_factory=dict)
    weather_info: Dict = field(default_factory=dict)
    panel_id: str = None
    server_communication_error: bool = None
    time_now: str = None

    def refresh_time(self):
        dt = datetime.now(tz.gettz(self.tz()))
        self.time_now = dt.strftime("%H:%M")
        return self.time_now

    def tz(self) -> str:
        return self.panel_info.get("idle-info", {}).get("timezone", DEFAULT_TIMEZONE)

    def __eq__(self, other):
        if not isinstance(other, PanelState):
            return False
        return (
            self.panel_id == other.panel_id
            and self.time_now == other.time_now
            and self.panel_info == other.panel_info
            and self.weather_info == other.weather_info
            and self.server_communication_error == other.server_communication_error
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


def write_to_file(state: PanelState):
    try:
        with open(PANEL_STATE_FILE, "wb") as f:
            as_json = orjson.dumps(
                state,
                option=orjson.OPT_NAIVE_UTC | orjson.OPT_INDENT_2,
            )
            f.write(as_json)
    except Exception as e:
        print(f"An error occurred during writing: {e}")


def read_from_file():
    try:
        with open(PANEL_STATE_FILE, "rb") as f:
            return PanelState.from_dict(orjson.loads(f.read()))
    except FileNotFoundError:
        _log.error(f"⚠️ State file not found: {PANEL_STATE_FILE}, returning empty state")
        return PanelState()
    except Exception as e:
        _log.error(f"⚠️ An error occurred during reading: {e}, returning empty state")
        return PanelState()
