from dataclasses import dataclass, field
from typing import Dict
from datetime import datetime
from dateutil import tz
import sevencourts.config as cfg


@dataclass
class PanelState:
    """
    Global infoboard state
    """

    saved_config: Dict = field(default_factory=dict)
    panel_info: Dict = field(default_factory=dict)
    weather_info: Dict = field(default_factory=dict)
    panel_id: str = None
    panel_info_fetch_failed: bool = None  # TODO review
    time_now: str = None

    def refresh_time(self):
        dt = datetime.now(tz.gettz(self.tz()))
        self.time_now = dt.strftime("%H:%M")
        return self.time_now

    def tz(self) -> str:
        idle_info = self.panel_info.get("idle-info", {})
        result = idle_info.get("timezone", self.saved_config.get("timezone"))
        return result or cfg.DEFAULT_TIMEZONE

    def __eq__(self, other):
        if not isinstance(other, PanelState):
            return False
        return (
            self.panel_id == other.panel_id
            and self.time_now == other.time_now
            and self.panel_info == other.panel_info
            and self.weather_info == other.weather_info
            and self.saved_config == other.saved_config
            and self.panel_info_fetch_failed == other.panel_info_fetch_failed
        )
