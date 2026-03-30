"""
System utils
"""

import sevencourts.logging as logging

_log = logging.logger("system")


def uptime():
    try:
        with open("/proc/uptime", "r") as f:
            return float(f.readline().split()[0])
    except Exception as ex:
        _log.debug("Cannot get uptime")
        return -1


def cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read().strip()) / 1000.0
    except Exception as ex:
        _log.debug("Cannot get CPU temperature")
        return -1
