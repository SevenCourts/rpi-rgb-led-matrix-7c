"""
IPC state reader for sevencourts-daemon.

Reads JSON state files written atomically by the daemon:
- BLE: /run/sevencourts/7c-ble-state.json
"""

from __future__ import annotations

from dataclasses import dataclass, field
import orjson
import os
import sevencourts.logging as logging

_log = logging.logger("daemon")

DAEMON_BLE_STATE_FILE = os.getenv(
    "DAEMON_BLE_STATE_FILE", "/run/sevencourts/7c-ble-state.json"
)


@dataclass
class BleState:
    event: str = ""  # "ble_client_connected", "ble_client_disconnected"
    address: str = ""
    name: str = ""
    alias: str = ""
    timestamp: int = 0


@dataclass
class DaemonState:
    ble: BleState = field(default_factory=BleState, compare=False)

    # Derived display field (set by polling thread)
    ble_status: str = ""


def read_json_file(path: str) -> dict | None:
    try:
        with open(path, "rb") as f:
            return orjson.loads(f.read())
    except FileNotFoundError:
        return None
    except Exception as e:
        _log.debug(f"Cannot read {path}: {e}")
        return None


def read_ble_state(path: str = DAEMON_BLE_STATE_FILE) -> BleState | None:
    raw = read_json_file(path)
    if raw is None:
        return None
    data = raw.get("data", {})
    return BleState(
        event=raw.get("event", ""),
        address=data.get("address", ""),
        name=data.get("name", ""),
        alias=data.get("alias", ""),
        timestamp=raw.get("timestamp", 0),
    )
