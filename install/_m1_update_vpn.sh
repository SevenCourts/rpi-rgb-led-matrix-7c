#!/bin/sh
# SevenCourts vpn update script

set -x

if [ $(id -u) -ne 0 ]
  then echo Please run this script as root or using sudo!
  exit
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo 'script dir:' $SCRIPT_DIR


cp $SCRIPT_DIR/7c-vpn/etc/openvpn/client/* /etc/openvpn/client/

mkdir -p /etc/systemd/system/openvpn-client@call-home.service.d/
cp $SCRIPT_DIR/7c-vpn/etc/systemd/system/openvpn-client@call-home.service.d/override.conf /etc/systemd/system/openvpn-client@call-home.service.d/

systemctl enable --now openvpn-client@call-home

# Clean-up old openvpn config
systemctl disable --now openvpn-client@callhome
rm -f /etc/openvpn/client/callhome.conf
rm -f /etc/systemd/system/openvpn-client@callhome.service.d/override.conf

echo '----------------------'
echo '7C-VPN UPDATED SUCCESSFULLY'