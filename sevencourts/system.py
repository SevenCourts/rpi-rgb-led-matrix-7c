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


def os_release(path="/etc/7c-os-release"):
    """Parse the Buildroot-stamped OS release file (key=value lines).

    Written into the rootfs at image build time by sevencourts.os
    (os/board/post-build.sh). Carries e.g.:
        os_commit / os_commit_full / rgbmatrix_commit / build_date / buildroot

    Returns {} if the file is missing or unreadable (e.g. local/dev), so callers
    can fall back to "unknown".
    """
    try:
        info = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    info[k.strip()] = v.strip()
        return info
    except Exception:
        _log.debug("Cannot read OS release file")
        return {}
