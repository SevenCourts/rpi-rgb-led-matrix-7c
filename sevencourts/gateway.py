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

# In container there is no git binary and history -- read from file.
# In local environment we don't want generate this file manually -- ask git.
try:
    with open("commit-id", "r") as file:
        GIT_COMMIT_ID = file.read().strip()
except:
    GIT_COMMIT_ID = (
        subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()
    )

try:
    with open("commit-date", "r") as file:
        GIT_COMMIT_DATE = file.read().strip()
except:
    GIT_COMMIT_DATE = (
        subprocess.check_output(["git", "show", "-s", "--format=%as", "HEAD"])
        .strip()
        .decode()
    )


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
            return (
                match or None
            )  # FIX: the server can return False if match is over, this leads to error then
        elif response.status == 205:
            idle_info = json.loads(response.read().decode("utf-8") or "null")
            _log.debug(f"idle-info: {idle_info}")
            return idle_info


def register_panel() -> str:
    """Return panel_id of the registered panel"""
    name = os.getenv("TABLEAU_PANEL_CODE", network.hostname())
    ip_address = network.ip_address()
    url = _url_panel_registration()
    _log.debug(f"Registering panel at: {url}")
    data = json.dumps(
        {
            "code": name,
            "ip": ip_address,
            "firmware_version": GIT_COMMIT_ID,
            "firmware_date": GIT_COMMIT_DATE,
        }
    ).encode("utf-8")
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
