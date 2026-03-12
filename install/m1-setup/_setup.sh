#!/bin/bash
# SevenCourts M1 installation script
#
# Usage: _setup.sh [BRANCH] [DAEMON_URL]
#   BRANCH     - firmware branch to checkout (default: firmware/stable)
#   DAEMON_URL - sevencourts-daemon download URL (default: dl.sevencourts.com latest)

set -euo pipefail
set -x

trap 'echo "SETUP FAILED at line $LINENO (exit code $?)" >&2' ERR

FIRMWARE_BRANCH="${1:-firmware/stable}"
DAEMON_URL="${2:-https://dl.sevencourts.com/s/gCYdoPfKEJCpawT/download}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run this script as root or using sudo!" >&2
  exit 1
fi

PANEL_TYPE="${PANEL_TYPE:-M1}"


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo 'script dir:' $SCRIPT_DIR

# Wait for any running apt/dpkg process to finish (e.g. unattended-upgrades after reboot)
echo 'Waiting for dpkg lock...'
while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do
  sleep 2
done
echo 'dpkg lock is free.'


echo '=== Phase 0: Clean up previous installations ==='

systemctl disable --now 7c-hostname 2>/dev/null || true
systemctl disable --now 7c 2>/dev/null || true
systemctl disable --now 7c-controller 2>/dev/null || true
systemctl disable --now 7c-d 2>/dev/null || true
rm -rf /opt/7c


echo '=== Phase 1: OS configuration ==='

# Set the country code (must do to enable WiFi)
## Find your country's code here: <https://en.wikipedia.org/wiki/ISO_3166-1>
raspi-config nonint do_wifi_country DE

# Change timezone
timedatectl set-timezone Europe/Berlin

# Turn off sound card
grep -qF "blacklist snd_bcm2835" /etc/modprobe.d/alsa-blacklist.conf 2>/dev/null \
  || echo "blacklist snd_bcm2835" >> /etc/modprobe.d/alsa-blacklist.conf

# Configure CPU isolation for real-time performance
## s. https://github.com/SevenCourts/rpi-rgb-led-matrix?tab=readme-ov-file#cpu-use
FILE="/boot/cmdline.txt"
STRING_TO_ADD=" isolcpus=3"  # Note the leading space for clean appending
grep -qF "$STRING_TO_ADD" "$FILE" || sed -i "s/$/$STRING_TO_ADD/" "$FILE"

# Setup RTC
## Below is the short version of the [article](https://pimylifeup.com/raspberry-pi-rtc/) on setting up RTC on Raspberry Pi.
raspi-config nonint do_i2c 0
grep -qF "dtoverlay=i2c-rtc,ds1307" /boot/config.txt 2>/dev/null \
  || echo "dtoverlay=i2c-rtc,ds1307" >> /boot/config.txt
apt-get -y remove fake-hwclock
update-rc.d -f fake-hwclock remove
cp $SCRIPT_DIR/7c-os/lib/udev/hwclock-set /lib/udev/hwclock-set


echo '=== Phase 2: Download ==='

apt-get update --allow-releaseinfo-change
apt-get install -y \
  git vim build-essential \
  python3-dev python3-pillow python3-requests python3-gpiozero python3-dateutil cython3 \
  python3-pip python3-smbus i2c-tools \
  openvpn

pip install orjson==3.10

# Clone and checkout rpi-rgb-led-matrix SDK
mkdir /opt/7c
cd /opt/7c
git clone https://github.com/sevencourts/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix/
git -c advice.detachedHead=false checkout sevencourts/v2 || { echo "FATAL: branch 'sevencourts/v2' not found in rpi-rgb-led-matrix repo" >&2; exit 1; }

# Clone and checkout firmware
cd /opt/7c/rpi-rgb-led-matrix/bindings/python
git clone https://github.com/SevenCourts/rpi-rgb-led-matrix-7c.git
cd /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c
git -c advice.detachedHead=false checkout "$FIRMWARE_BRANCH" -- || { echo "FATAL: branch '$FIRMWARE_BRANCH' not found in rpi-rgb-led-matrix-7c repo" >&2; exit 1; }

# Download sevencourts-daemon
cd /opt/7c
curl -fL -o sevencourts-daemon.zip "$DAEMON_URL"
# TODO: add checksum verification (sha256sum -c "$SCRIPT_DIR/sevencourts-daemon.zip.sha256")
file sevencourts-daemon.zip | grep -q "Zip archive" \
  || { echo "FATAL: downloaded file is not a valid zip archive (check DAEMON_URL)" >&2; exit 1; }
unzip sevencourts-daemon.zip
chmod u+x sevencourts-daemon


echo '=== Phase 3: Build ==='

cd /opt/7c/rpi-rgb-led-matrix
make -C lib
make -C bindings/python/rgbmatrix
cd bindings/python
$(command -v python3) setup.py install


echo '=== Phase 4: Install & configure ==='

# Create a symlink for convenient access to the firmware directory
ln -s /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c/ /root/7c-firmware

# Create 7c offline state file
rm -f /opt/7c/panel.conf # remove previous config if any
touch /opt/7c/last_panel_state.json
chmod 666 /opt/7c/last_panel_state.json

# Set up 7c hostname systemd service
cp $SCRIPT_DIR/7c-os/opt/7c/7c-set-hostname.sh /opt/7c/7c-set-hostname.sh
chmod u+x /opt/7c/7c-set-hostname.sh
cp $SCRIPT_DIR/7c-os/etc/systemd/system/7c-hostname.service /etc/systemd/system/7c-hostname.service
systemctl enable 7c-hostname

# Set up 7c systemd service
cp $SCRIPT_DIR/7c-os/etc/systemd/system/7c-${PANEL_TYPE,,}.service /etc/systemd/system/7c.service
systemctl enable 7c

# Set up sevencourts-daemon systemd service
cp $SCRIPT_DIR/7c-os/etc/systemd/system/7c-d.service /etc/systemd/system/7c-d.service
systemctl enable 7c-d

# Install 'Call Home' VPN
## Full documentation: see the [Wiki page](https://wiki.suprematic.team/books/tennis-cast-scoreboard/page/call-home-vpn-for-7c-scoreboard).
mkdir -p /root/.ssh/
cp $SCRIPT_DIR/7c-vpn/ssh/authorized_keys /root/.ssh/authorized_keys
cp $SCRIPT_DIR/7c-vpn/etc/openvpn/client/* /etc/openvpn/client/
mkdir -p /etc/systemd/system/openvpn-client@call-home.service.d/
cp $SCRIPT_DIR/7c-vpn/etc/systemd/system/openvpn-client@call-home.service.d/override.conf /etc/systemd/system/openvpn-client@call-home.service.d/
systemctl enable openvpn-client@call-home


echo '----------------------'
echo 'SUCCESSFULLY INSTALLED'

reboot
