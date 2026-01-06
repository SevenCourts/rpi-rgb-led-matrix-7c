#!/bin/sh
# SevenCourts M1 installation script

set -x

if [ $(id -u) -ne 0 ]
  then echo Please run this script as root or using sudo!
  exit
fi

# 0. clean-up previous installations
systemctl disable --now 7c-hostname
systemctl disable --now 7c
systemctl disable --now 7c-controller
rm -rf /opt/7c

set -e

# Set the country code (must do to enable WiFi)
## Find your country's code here: <https://en.wikipedia.org/wiki/ISO_3166-1>
raspi-config nonint do_wifi_country DE

# Change timezone
timedatectl set-timezone Europe/Berlin

# Turn off sound card
echo "blacklist snd_bcm2835" >> /etc/modprobe.d/alsa-blacklist.conf


# Install dependencies
apt-get update --allow-releaseinfo-change
apt-get install git vim build-essential -y

# Install and make rpi-rgb-led-matrix SDK
mkdir /opt/7c
cd /opt/7c
git clone https://github.com/sevencourts/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix/
git checkout sevencourts/v2
make

# Install and make python3 bindings
apt-get install python3-dev python3-pillow python3-requests python3-gpiozero python3-dateutil cython3 -y
make build-python PYTHON=$(command -v python3)
make install-python PYTHON=$(command -v python3)

apt-get install python3-pip -y
pip install orjson==3.10

# Install rpi-rgb-led-matrix-7c
cd /opt/7c/rpi-rgb-led-matrix/bindings/python
git clone https://github.com/SevenCourts/rpi-rgb-led-matrix-7c.git
cd /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c
git checkout firmware/stable

# Configure CPU isolation for real-time performance
## s. https://github.com/SevenCourts/rpi-rgb-led-matrix?tab=readme-ov-file#cpu-use
FILE="/boot/cmdline.txt"
STRING_TO_ADD=" isolcpus=3"  # Note the leading space for clean appending
# Check if the string exists; if NOT (!), execute the sed command
grep -qF "$STRING_TO_ADD" "$FILE" || sed -i "s/$/$STRING_TO_ADD/" "$FILE"

# Create a symlink for convenient access to the firmware directory
ln -s /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c/ /root/7c-firmware

# Create 7c offline state file
rm -f /opt/7c/panel.conf # remove previous config if any
touch /opt/7c/last_panel_state.json
chmod 666 /opt/7c/last_panel_state.json

# Set up 7c hostname systemd service
cp 7c-os/opt/7c/7c-set-hostname.sh /opt/7c/7c-set-hostname.sh
chmod u+x /opt/7c/7c-set-hostname.sh
cp 7c-os/etc/systemd/system/7c-hostname.service /etc/systemd/system/7c-hostname.service
systemctl enable 7c-hostname

# Set up 7c systemd service
cp 7c-os/etc/systemd/system/7c.service /etc/systemd/system/7c.service
systemctl enable 7c

# Install 7c-controller
## ***TODO migrate source code and build for the 7c-controller (Rust project)***
cd /opt/7c
## ***FIXME suprematic***
curl -o 7c_m1_controller.zip https://dl.suprematic.net/index.php/s/YHWrGCaJ42XTpdx/download
unzip 7c_m1_controller.zip
chmod u+x 7c_m1_controller
cd /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c
cp 7c-os/etc/systemd/system/7c-controller.service /etc/systemd/system/7c-controller.service
systemctl enable 7c-controller

# Setup RTC
## Below is the short version of the [article](https://pimylifeup.com/raspberry-pi-rtc/) on setting up RTC on Raspberry Pi.
raspi-config nonint do_i2c 0
apt-get install python3-smbus i2c-tools -y
echo "dtoverlay=i2c-rtc,ds1307" >> /boot/config.txt
apt-get -y remove fake-hwclock
update-rc.d -f fake-hwclock remove
cp 7c-os/lib/udev/hwclock-set /lib/udev/hwclock-set

# Install 'Call Home' VPN
##  ***FIXME suprematic => gDocs ***
## Full documentation: see the [Wiki page](https://wiki.suprematic.team/books/tennis-cast-scoreboard/page/call-home-vpn-for-7c-scoreboard).
apt-get install openvpn -y
mkdir -p /root/.ssh/
cp 7c-vpn/ssh/authorized_keys /root/.ssh/authorized_keys
cp 7c-vpn/etc/openvpn/client/callhome.conf /etc/openvpn/client/callhome.conf
mkdir -p /etc/systemd/system/openvpn-client@callhome.service.d/
cp 7c-vpn/etc/systemd/system/openvpn-client@callhome.service.d/override.conf /etc/systemd/system/openvpn-client@callhome.service.d/override.conf
systemctl enable openvpn-client@callhome

echo '----------------------'
echo 'SUCCESSFULLY INSTALLED'

reboot