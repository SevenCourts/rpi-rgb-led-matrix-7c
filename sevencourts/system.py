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


# FIXME wtf?! without this call, getting CPU temperature fails when is called from within class instance
try:
    from gpiozero import CPUTemperature  # type: ignore

    print(CPUTemperature().temperature)
except Exception as ex:
    _log.debug("Cannot get initial CPU temperature")


def cpu_temperature():
    try:
        from gpiozero import CPUTemperature  # type: ignore

        return CPUTemperature().temperature
    except Exception as ex:
        _log.debug("Cannot get CPU temperature")
        return -1
