from dataclasses import dataclass, field, fields
from typing import Dict
from datetime import datetime
from dateutil import tz
import ctypes
import ctypes.util
import fcntl
import struct
import time
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
    """Read RTC twice 100ms apart; if time advanced, the RTC is alive."""
    try:
        with open('/dev/rtc0', 'rb') as f:
            RTC_RD_TIME = 0x80247009
            buf = bytearray(36)
            fcntl.ioctl(f, RTC_RD_TIME, buf)
            t1 = struct.unpack_from('9i', buf)
            time.sleep(0.1)
            fcntl.ioctl(f, RTC_RD_TIME, buf)
            t2 = struct.unpack_from('9i', buf)
            ticking = t2 > t1
            _log.debug(f"RTC ticking check: t1={t1[:6]}, t2={t2[:6]}, ticking={ticking}")
            return ticking
    except Exception as e:
        _log.debug(f"RTC not available: {e}")
        return False


def _is_ntp_synchronized() -> bool:
    """
    Check if the kernel clock has been synchronized by any NTP daemon.
    Uses adjtimex() to read kernel clock status — works with both
    systemd-timesyncd (M1/legacy) and BusyBox ntpd (L1/sevencourts.os).
    Returns True when the STA_UNSYNC bit (0x0040) is cleared.
    """
    # TODO: test on L1 hardware (BusyBox ntpd) to confirm STA_UNSYNC is cleared after sync
    try:
        synced = _is_kernel_clock_synced()
        _log.debug(f"NTP synchronized (adjtimex): {synced}")
        return synced
    except Exception as e:
        _log.debug(f"adjtimex check failed: {e}, falling back to sentinel file")
        # Fallback for systems where adjtimex is unavailable
        synced = os.path.exists('/run/systemd/timesync/synchronized')
        _log.debug(f"NTP synchronized (sentinel): {synced}")
        return synced


STA_UNSYNC = 0x0040


def _is_kernel_clock_synced() -> bool:
    """
    Call adjtimex() to check if the kernel clock is synchronized.
    Both ntpd and systemd-timesyncd clear the STA_UNSYNC bit once synced.
    """
    libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

    # struct timex — we only need the `status` field (offset 4 on both 32/64-bit)
    # Full struct is large; allocate 256 bytes to be safe.
    buf = ctypes.create_string_buffer(256)
    # modes = 0 (ADJ_OFFSET_SS_READ — read-only query)
    struct.pack_into('i', buf, 0, 0)
    ret = libc.adjtimex(buf)
    if ret == -1:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
    status = struct.unpack_from('i', buf, 4)[0]
    return (status & STA_UNSYNC) == 0


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
