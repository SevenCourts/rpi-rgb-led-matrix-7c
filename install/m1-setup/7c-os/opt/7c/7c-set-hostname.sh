#!/bin/bash
# DEPRECATED: Legacy version for SystemD-based panels.
# Canonical version: sevencourts.os/os/board/rootfs_overlay/opt/7c/7c-set-hostname.sh
name=`cat /sys/firmware/devicetree/base/serial-number | tail -c +9`

# this is used by Python script, 7c-d (at least)
hostname $name

# this is used by Bluetooth, s. /etc/bluetooth/main.conf
echo 'PRETTY_HOSTNAME='$name > /etc/machine-info

echo 'Set hostname to '$name | systemd-cat -p info
