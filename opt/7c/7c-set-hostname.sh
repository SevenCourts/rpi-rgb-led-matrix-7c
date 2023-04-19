#!/bin/bash
name=`cat /sys/firmware/devicetree/base/serial-number | tail -c +9`
hostname $name
echo 'Set hostname to '$name | systemd-cat -p info
