"""
Start-up config utils
"""

import os
import sevencourts.logging as logging

_log = logging.logger("config")

DEFAULT_TIMEZONE = "Europe/Berlin"

PANEL_CONFIG_FILE = os.getenv("PANEL_CONFIG")


def read():
    _log.debug(f"Reading config from '{PANEL_CONFIG_FILE}'")
    result = {}
    if PANEL_CONFIG_FILE:
        lines = []
        try:
            with open(PANEL_CONFIG_FILE, "r") as file:
                lines = list(
                    filter(lambda x: len(x.strip()) > 0, file.read().splitlines())
                )
        except:
            pass
        if lines:
            result = {k: v for k, v in map(lambda x: x.split("=", 1), lines)}
    _log.info(f"Config: '{result}'")
    return result


def write(config):
    _log.debug(f"Writing config to '{PANEL_CONFIG_FILE}'")
    if PANEL_CONFIG_FILE:
        conf = []
        for k, v in config.items():
            value = "" if v is None else str(v)
            conf.append(k + "=" + value)
        try:
            with open(PANEL_CONFIG_FILE, "w") as file:
                file.write("\n".join(conf))
        except:
            pass
