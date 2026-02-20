"""
IPC state reader for sevencourts-daemon.

Reads JSON state files written atomically by the daemon:
- BLE: /run/sevencourts/7c-ble-state.json
- Network: /run/sevencourts/7c-network-state.json
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import orjson
import os
import sevencourts.logging as logging

_log = logging.logger("daemon")

DAEMON_BLE_STATE_FILE = os.getenv(
    "DAEMON_BLE_STATE_FILE", "/run/sevencourts/7c-ble-state.json"
)

DAEMON_NETWORK_STATE_FILE = os.getenv(
    "DAEMON_NETWORK_STATE_FILE", "/run/sevencourts/7c-network-state.json"
)


@dataclass
class BleState:
    event: str = ""  # "ble_client_connected", "ble_client_disconnected"
    address: str = ""
    name: str = ""
    alias: str = ""
    timestamp: int = 0


@dataclass
class NetworkState:
    event: str = ""  # "connecting", "connected", "disconnected"
    interface: str = ""  # "wifi", "ethernet"
    ssid: str = ""
    ip_address: str = ""
    reason: str = ""  # disconnect reason: auth_rejected, network_not_found, etc.
    encryption: str = ""
    timestamp: int = 0


class OverlayPhase(Enum):
    HIDDEN = "hidden"
    BLE_CONNECTED = "ble_connected"
    WIFI_CONNECTING = "wifi_connecting"
    WIFI_OK = "wifi_ok"
    WIFI_FAIL = "wifi_fail"


# Human-readable disconnect reasons
DISCONNECT_REASONS = {
    "auth_rejected": "Wrong password",
    "network_not_found": "Network not found",
    "server_unreachable": "No internet",
    "disconnected": "Connection lost",
}


@dataclass
class DaemonState:
    ble: BleState = field(default_factory=BleState, compare=False)
    network: NetworkState = field(default_factory=NetworkState, compare=False)

    # Overlay display fields (set by polling thread, drive redraw)
    overlay_phase: OverlayPhase = OverlayPhase.HIDDEN
    overlay_text: str = ""  # primary: "Connected to Phone", "Connecting to MyNet..."
    overlay_detail: str = ""  # secondary: IP address, error reason
    overlay_ssid: str = ""  # SSID shown on its own row
    blink_tick: bool = False  # toggles each poll during WIFI_CONNECTING

    # Persistent indicator (independent of overlay)
    wifi_error: bool = False


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


def read_network_state(path: str = DAEMON_NETWORK_STATE_FILE) -> NetworkState | None:
    raw = read_json_file(path)
    if raw is None:
        return None
    data = raw.get("data", {})
    if not data:
        return None
    return NetworkState(
        event=raw.get("event", ""),
        interface=data.get("interface", ""),
        ssid=data.get("ssid", ""),
        ip_address=data.get("ip_address", ""),
        reason=data.get("reason", ""),
        encryption=data.get("encryption", ""),
        timestamp=raw.get("timestamp", 0),
    )
