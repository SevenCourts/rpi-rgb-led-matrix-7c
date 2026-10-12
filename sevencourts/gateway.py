"""
Gateway to SevenCourts server API
"""

import os
import json
import urllib.request  # Standard lib, low-level
import requests  # 3rd party lib, higher-level
from datetime import datetime
from dateutil import tz
import subprocess
import sevencourts.system as sys
import sevencourts.network as network
import sevencourts.logging as logging

DEFAULT_TIMEZONE = "Europe/Berlin"

_log = logging.logger("gateway")

# In container/production there is no git binary and history -- read from file.
# In local environment we don't want generate this file manually -- ask git.
# If neither file nor git is available, fall back to "unknown".
def _read_commit_info(filename, git_args):
    try:
        with open(filename, "r") as file:
            return file.read().strip()
    except Exception:
        pass
    try:
        return subprocess.check_output(git_args).strip().decode()
    except Exception:
        return "unknown"

GIT_COMMIT_ID = _read_commit_info("commit-id", ["git", "rev-parse", "HEAD"])
GIT_COMMIT_DATE = _read_commit_info("commit-date", ["git", "show", "-s", "--format=%as", "HEAD"])


TIMEOUT_S = 10

BASE_URL = os.getenv("TABLEAU_SERVER_BASE_URL", "https://prod.tableau.tennismath.com")


def _url_panel_registration():
    return BASE_URL + "/panels/"


def _url_panel_info(panel_id):
    return BASE_URL + "/panels/" + panel_id + "/match"


def _url(path):
    return BASE_URL + "/" + path


def fetch_panel_info(panel_id):
    url = _url_panel_info(panel_id)
    req = urllib.request.Request(url)
    req.add_header(
        "7C-Is-Panel-Preview", "false"
    )  # FIXME is to be set to 'true' when started as emulator within panel admin web UI
    req.add_header("7C-Uptime", str(sys.uptime()))
    req.add_header("7C-CPU-Temperature", str(sys.cpu_temperature()))
    req.add_header("7C-Time", datetime.now(tz.gettz(DEFAULT_TIMEZONE)).isoformat())
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as response:
        _log.debug(f"url='{url}', status={str(response.status)}")
        if response.status == 200:
            match = json.loads(response.read().decode("utf-8"))
            _log.debug(f"match: {match}")
            # The server can return false when a match is over, and a fresh
            # panel can get an empty body. Callers only handle a dict.
            return _as_panel_info(match)
        elif response.status == 205:
            idle_info = json.loads(response.read().decode("utf-8") or "null")
            _log.debug(f"idle-info: {idle_info}")
            return _as_panel_info(idle_info)
        return {}


def _as_panel_info(body) -> dict:
    """The server's answer as a dict; anything else (false, null, a list) as {}."""
    return body if isinstance(body, dict) else {}


def _panel_type() -> str:
    """The form factor this process draws for, as sevencourts/m1/dimens.py reads it."""
    panel_type = os.environ.get("PANEL_TYPE", "M1")
    return panel_type if panel_type in ("L1", "XL1") else "M1"


def _registration_body() -> dict:
    # OS image provenance, stamped into /etc/7c-os-release at build time.
    # TODO: also report the running daemon version -- see TODO-report-daemon-version.md
    os_info = sys.os_release()
    return {
        "code": os.getenv("TABLEAU_PANEL_CODE", network.hostname()),
        "ip": network.ip_address(),
        # tun0 address (10.8.1.x) -- the one operators can reach via
        # vpn.sevencourts.com; null when the tunnel is down.
        "vpn_ip": network.vpn_ip_address(),
        # M1 / L1 / XL1 -- the server has no other way to know the canvas size.
        "panel_type": _panel_type(),
        "firmware_version": GIT_COMMIT_ID,
        "firmware_date": GIT_COMMIT_DATE,
        "os_version": os_info.get("os_commit_full", "unknown"),
        "os_buildroot": os_info.get("buildroot", "unknown"),
        "os_build_date": os_info.get("build_date", "unknown"),
        "rgbmatrix_version": os_info.get("rgbmatrix_commit", "unknown"),
    }


def register_panel() -> str:
    """Return panel_id of the registered panel"""
    url = _url_panel_registration()
    _log.debug(f"Registering panel at: {url}")
    data = json.dumps(_registration_body()).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("7C-Time", datetime.now(tz.gettz(DEFAULT_TIMEZONE)).isoformat())
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        _json = json.loads(response.read().decode("utf-8"))
        _log.debug(f"Registered: {url} - '{_json}'")
        return _json["id"]


def head_by_path(image_path):
    url = _url(image_path)
    return head(url)


def get_raw_by_path(image_path):
    url = _url(image_path)
    return get_raw(url)


def head(url):
    request = urllib.request.Request(url, method="HEAD")
    response = urllib.request.urlopen(request, timeout=TIMEOUT_S)
    return response


def get_raw(url):
    return requests.get(url, stream=True).raw
