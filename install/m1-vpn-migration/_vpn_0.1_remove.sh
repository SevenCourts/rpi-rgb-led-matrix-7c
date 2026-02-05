#!/bin/sh
# SevenCourts vpn update script

set -x

if [ $(id -u) -ne 0 ]
  then echo Please run this script as root or using sudo!
  exit
fi


# Clean-up old openvpn config
systemctl disable --now openvpn-client@callhome
rm -f /etc/openvpn/client/callhome.conf
rm -f /etc/systemd/system/openvpn-client@callhome.service.d/override.conf

echo '----------------------'
echo '7C-VPN 0.1 REMOVED SUCCESSFULLY'