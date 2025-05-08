#!/bin/sh

# SevenCourts M1 installation script

if [ $(id -u) -ne 0 ]
  then echo Please run this script as root or using sudo!
  exit
fi

# Set the country code (must do to enable WiFi)
## Find your country's code here: <https://en.wikipedia.org/wiki/ISO_3166-1>

raspi-config nonint do_wifi_country DE

# Change timezone

timedatectl set-timezone Europe/Berlin

# Install dependencies

apt update
apt install git vim build-essential -y

# Install and make rpi-rgb-led-matrix SDK

mkdir /opt/7c
cd /opt/7c
git clone https://github.com/sevencourts/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix/
git checkout 7c/m1/dev
make

# Create 7c config file

touch /opt/7c/panel.conf
chmod 666 /opt/7c/panel.conf

# Install and make python3 bindings

sudo apt-get update --allow-releaseinfo-change && sudo apt-get install python3-dev python3-pillow python3-requests python3-gpiozero python3-dateutil -y
make build-python PYTHON=$(command -v python3)
sudo make install-python PYTHON=$(command -v python3)

# Install rpi-rgb-led-matrix-7c
## TODO: check if we need to keep the directory structure?

cd /opt/7c/rpi-rgb-led-matrix/bindings/python
git clone https://github.com/SevenCourts/rpi-rgb-led-matrix-7c.git
git switch firmware/stable

# Turn off sound card

echo "blacklist snd_bcm2835" >> /etc/modprobe.d/alsa-blacklist.conf

# Set up 7c hostname systemd service

cd /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c
cp 7c-os/opt/7c/7c-set-hostname.sh /opt/7c/7c-set-hostname.sh
chmod u+x /opt/7c/7c-set-hostname.sh
cp 7c-os/etc/systemd/system/7c-hostname.service /etc/systemd/system/7c-hostname.service
systemctl enable 7c-hostname

# Set up 7c systemd services

cp 7c-os/etc/systemd/system/7c.service /etc/systemd/system/7c.service
cp 7c-os/etc/systemd/system/7c-demo.service /etc/systemd/system/7c-demo.service

# Enable service and start now:

systemctl enable --now 7c.service

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

# Install 'Call Home' VPN
##  ***FIXME suprematic => gDocs ***
## Full documentation: see the [Wiki page](https://wiki.suprematic.team/books/tennis-cast-scoreboard/page/call-home-vpn-for-7c-scoreboard).

apt-get install openvpn -y
mkdir -p /root/.ssh/
cp 7c-vpn/ssh/authorized_keys /root/.ssh/authorized_keys
cp 7c-vpn/etc/openvpn/client/callhome.conf /etc/openvpn/client/callhome.conf
mkdir -p /etc/systemd/system/openvpn-client@callhome.service.d/
cp 7c-vpn/etc/systemd/system/openvpn-client@callhome.service.d/override.conf /etc/systemd/system/openvpn-client@callhome.service.d/override.conf
systemctl daemon-reload
systemctl enable --now openvpn-client@callhome

# Setup RTC
## Below is the short version of the [article](https://pimylifeup.com/raspberry-pi-rtc/) on setting up RTC on Raspberry Pi.
raspi-config nonint do_i2c 0
apt -y install python3-smbus i2c-tools
echo "dtoverlay=i2c-rtc,ds1307" >> /boot/config.txt
apt -y remove fake-hwclock
update-rc.d -f fake-hwclock remove
cp 7c-os/lib/udev/hwclock-set lib/udev/hwclock-set
