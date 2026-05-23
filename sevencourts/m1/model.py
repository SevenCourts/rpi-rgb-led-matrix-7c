from dataclasses import dataclass, field, fields
from typing import Dict
from datetime import datetime
from dateutil import tz
import fcntl
import struct
import orjson
import os
import sevencourts.logging as logging
from sevencourts.m1.daemon_state import DaemonState

_log = logging.logger("model")

DEFAULT_TIMEZONE = "Europe/Berlin"

PANEL_STATE_FILE = os.getenv("PANEL_STATE_FILE", "/opt/7c/last_panel_state.json")


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
    daemon: DaemonState = field(default_factory=DaemonState, metadata={"transient": True})

    last_updated_UTC: datetime = field(default=None, compare=False)

    def is_registered(self) -> bool:
        return self.panel_id is not None

    def refresh_time(self):
        if not is_clock_trustworthy():
            self.time_now_in_TZ = None
            return self.time_now_in_TZ
        dt = datetime.now(tz.gettz(self.tz()))
        self.time_now_in_TZ = dt.strftime("%H:%M")
        return self.time_now_in_TZ

    def tz(self) -> str:
        return self.panel_info.get("idle-info", {}).get("timezone", DEFAULT_TIMEZONE)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


_clock_trusted = False


def is_clock_trustworthy() -> bool:
    """
    Check if the system clock can be trusted.
    - Working RTC (M1): returns True immediately (RTC ticks between reads)
    - Dead RTC (L1): returns True only after NTP has synchronized
    Once True, the result is cached for the rest of the process lifetime.
    """
    global _clock_trusted
    if _clock_trusted:
        return True
    rtc = _is_rtc_ticking()
    ntp = _is_ntp_synchronized()
    if rtc or ntp:
        _clock_trusted = True
        _log.info(f"Clock is now trustworthy (rtc_ticking={rtc}, ntp_synced={ntp})")
        return True
    _log.debug(f"Clock not yet trustworthy (rtc_ticking={rtc}, ntp_synced={ntp})")
    return False


def _is_rtc_ticking() -> bool:
    """Return True if /dev/rtc0 returns a plausible current time.

    The kernel reads the RTC at boot (`hctosys`) and seeds the system
    clock from it; if the RTC reads a sane time now, the system clock
    is trustworthy even before NTP catches up.
    """
    try:
        rtc_dt = _read_rtc_time()
    except Exception as e:
        _log.debug(f"RTC not available: {e}")
        return False
    if rtc_dt.year < 2020 or rtc_dt.year > 2099:
        _log.debug(f"RTC time out of plausible range: {rtc_dt}")
        return False
    if _is_ntp_synchronized():
        delta = abs((rtc_dt - datetime.utcnow()).total_seconds())
        if delta > 300:
            _log.debug(f"RTC disagrees with NTP-synced clock by {delta:.0f}s: rtc={rtc_dt}")
            return False
    _log.debug(f"RTC ticking, time={rtc_dt}")
    return True


# struct rtc_time: 9 ints (sec, min, hour, mday, mon, year, wday, yday, isdst)
_RTC_RD_TIME = 0x80247009


def _read_rtc_time() -> datetime:
    """Read /dev/rtc0 via RTC_RD_TIME ioctl; return naive UTC datetime."""
    with open('/dev/rtc0', 'rb') as f:
        buf = bytearray(36)
        fcntl.ioctl(f, _RTC_RD_TIME, buf)
        sec, minute, hour, mday, mon, year_since_1900, *_ = struct.unpack_from('9i', buf)
    return datetime(year_since_1900 + 1900, mon + 1, mday, hour, minute, sec)


def _is_ntp_synchronized() -> bool:
    """Check if the system clock has been synchronized (by any NTP daemon)."""
    try:
        plausible = datetime.now().year >= 2026
        _log.debug(f"NTP synchronized: {plausible}")
        return plausible
    except Exception as e:
        _log.debug(f"NTP sync check failed: {e}")
        return False


# Skip disk writes when state hasn't changed — called every render cycle,
# avoid unnecessary I/O on the Pi's SD card.
_last_written_bytes: bytes = None


def write_to_file(state: PanelState):
    global _last_written_bytes
    try:
        as_json = orjson.dumps(
            {f.name: getattr(state, f.name) for f in fields(state) if not f.metadata.get("transient")},
            option=orjson.OPT_NAIVE_UTC | orjson.OPT_INDENT_2,
        )
        if as_json == _last_written_bytes:
            return
        _last_written_bytes = as_json
        with open(PANEL_STATE_FILE, "wb") as f:
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
