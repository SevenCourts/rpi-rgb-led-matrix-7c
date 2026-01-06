#!/bin/bash
name=`cat /sys/firmware/devicetree/base/serial-number | tail -c +9`

# this is used by Python script, 7c-controller (at least)
hostname $name

# this is used by Bluetooth, s. /etc/bluetooth/main.conf
echo 'PRETTY_HOSTNAME='$name > /etc/machine-info

echo 'Set hostname to '$name | systemd-cat -p info
