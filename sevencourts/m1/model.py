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
    Global M1 infoboard state
    """

    panel_info: Dict = field(default_factory=dict)
    weather_info: Dict = field(default_factory=dict)
    panel_id: str = None
    server_communication_error: bool = None
    time_now_in_TZ: str = None

    last_updated_UTC: datetime = field(default=None, compare=False)

    def refresh_time(self):
        dt = datetime.now(tz.gettz(self.tz()))
        self.time_now_in_TZ = dt.strftime("%H:%M")
        return self.time_now_in_TZ

    def tz(self) -> str:
        return self.panel_info.get("idle-info", {}).get("timezone", DEFAULT_TIMEZONE)

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
