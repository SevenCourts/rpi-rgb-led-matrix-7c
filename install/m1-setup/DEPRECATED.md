# DEPRECATED: Legacy Raspberry Pi OS Provisioning

This directory contains the legacy panel provisioning path for panels running
stock Raspberry Pi OS with SystemD.

**New panels use [sevencourts.os](https://github.com/SevenCourts/sevencourts.os)**
-- a custom Buildroot-based Linux image that ships everything pre-built:
BusyBox init (not SystemD), atomic app updates via tarballs, and all OS-level
configuration baked into the image at build time.

## What's here and where it moved

| Legacy (this directory)                        | New home (sevencourts.os)                                    |
|------------------------------------------------|--------------------------------------------------------------|
| `_setup.sh` (apt install, git clone, build)    | Buildroot image builds everything at image creation time     |
| `7c-os/etc/systemd/system/7c.service`          | `os/board/rootfs_overlay/etc/init.d/S10sevencourts`          |
| `7c-os/etc/systemd/system/7c-d.service`        | `os/board/rootfs_overlay/etc/init.d/S98daemon`               |
| `7c-os/etc/systemd/system/7c-hostname.service` | `os/board/rootfs_overlay/etc/init.d/S05hostname`             |
| `7c-os/opt/7c/7c-set-hostname.sh`              | `os/board/rootfs_overlay/opt/7c/7c-set-hostname.sh`          |
| `7c-vpn/` (SystemD openvpn-client@)            | `os/board/rootfs_overlay/etc/openvpn/callhome.conf.template` |
| OS config (isolcpus, RTC, sound blacklist)      | `os/board/boot/cmdline.txt`, `config.txt`, kernel fragment   |

## When to still use this

Only for maintaining the handful of legacy panels that were provisioned with
stock Raspberry Pi OS before the sevencourts.os image existed. Do not use
`_setup.sh` for new panel deployments.
