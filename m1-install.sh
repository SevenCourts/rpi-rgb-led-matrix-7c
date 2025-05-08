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

## ***TODO migrate source code and build for the 7c-controller***

cd /opt/7c
## ***FIXME suprematic***
curl -o 7c_m1_controller.zip https://dl.suprematic.net/index.php/s/YHWrGCaJ42XTpdx/download
unzip 7c_m1_controller.zip
chmod u+x 7c_m1_controller

cd /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c
cp 7c-os/etc/systemd/system/7c-controller.service /etc/systemd/system/7c-controller.service
systemctl enable 7c-controller

# Install 'Call Home' VPN
##  ***FIXME suprematic***
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

## Tests

The board is connected to Ethernet.

```shell
reboot
```

=> The panel should display the current time and the blue dot.

```shell
ssh user@<ip-address>
sudo -i
```

### Validate and register the hostname

```shell
hostname
```

Should output the last 8 bytes of `/sys/firmware/devicetree/base/serial-number` file contents.

Insert the hostname into the "Hostname" column of <https://docs.google.com/spreadsheets/d/1ewMfZ9fwiHdyakF1-PI1sjMTP-t4OwbRadxDGT6VGtM/edit#gid=696316085> spreadsheet.

### Check the 'Call home VPN' log

```shell
journalctl -e -u openvpn-client@callhome
journalctl -f -u openvpn-client@callhome
```

### Connect to the panel via "Call home VPN" server

- Login to `7c-vpn.sevencourts.com` via SSH using personal LDAP credentials

```shell
sudo -i
./7c.sh
```

Should display the list of scoreboards: hostnames together with their respective IP addresses as they are accessible from the 7c-vpn server.

```shell
10.8.0.4
7C-M1-R2
---
10.8.0.2
7C-M1-R3
---
```

Connect to the chosen scoreboard via SSH from `7c-vpn.sevencourts.com`:

```shell
ssh 10.8.0.4
```

### Test RTC-relevant values

Check kernel module is loaded with `sudo i2cdetect -y 1` -- the ouput table
will have `UU` on cross of `60` row and `8` column.

```txt
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:                         -- -- -- -- -- -- -- --
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    60: -- -- -- -- -- -- -- -- UU -- -- -- -- -- -- --
    70: -- -- -- -- -- -- -- --
```

1. Check RTC time is correct
    1. Show the current time from RTC with `hwclock --show`.
    1. If the time differs from the actual time, wait until OS time is synced, and
    actualize RTC clock time with `hwclock --systohc`.
1. Test that the setup was done correctly
    1. Remember the current time (hh:mm) and turn off the panel with `sudo shutdown`.
    1. Wait 3 minutes, turn on the panel, and after around 18 seconds panel
    displays the actual (hh:mm + 3 minutes) time.

### Final test

Disconnect from Ethernet, reboot.

=> The panel should display current time and the blue dot.

### Test WiFi setting

- Open "SevenCourts Admin" iOS app
- Connect the panel to a WiFi network

=> The panel should display current time and no blue dot.

Reboot. The panel should display:

=> ~15 seconds of black screen
=> ~5 second current time and the blue dot
=> current time only

## Update Firmware

***FIXME suprematic***

- Login to `7c-vpn.suprematic.team` via SSH using personal LDAP credentials

```shell
sudo -i
./7c.sh
```

Should display the list of scoreboards: hostnames together with their respective IP addresses as they are accessible from the 7c-vpn server.

```shell
10.8.0.4
7C-M1-R2
---
10.8.0.2
7C-M1-R3
---
```

Start update script for each panel, e.g.:

```shell
./7c-update-panel.sh 10.8.0.2
```

## Switch stage [PROD|STAGING|DEV]

Stop the 7c service:

```shell
EDITOR=vim systemctl edit 7c
```

Before the `### Lines below this comment will be discarded`, configure the `TABLEAU_SERVER_BASE_URL` environment variable with the server URL:

```shell
[Service]
Environment=PANEL_CONFIG=/opt/7c/panel.conf TABLEAU_SERVER_BASE_URL=<URL>
```

URLs:

- DEV: <https://dev.server.sevencourts.com>
- STAGING: <https://staging.server.sevencourts.com>
- PROD: <https://prod.server.sevencourts.com>

For PROD, this section can be removed, since the PROD URL is default.

If needed, switch the firmware branch:

```shell
cd /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c/
git fetch
git switch <branch>
```

Restart the 7c service:

```shell
systemctl daemon-reload
systemctl restart 7c
```

### WiFi settings

#### With SevenCourts Admin app

TODO: where to download for Android / iOS

#### With 7c-controller.service config

Being logged in via SSH to the device:

```shell
echo "{\"ssid\":\"<SSID>\",\"psk\":\"<PSK>\"}" > /etc/7c_m1_assoc.json
```

#### With raspi-config in non-interactive mode (CLI)

```shell
raspi-config nonint do_wifi_ssid_passphrase <SSID> <PSK>
```

#### Misc RaspiOS Lite commands

Rasp-config command line parameters:

- <https://forums.raspberrypi.com/viewtopic.php?t=21632>
- <https://loganmarchione.com/2021/07/raspi-configs-mostly-undocumented-non-interactive-mode/>

```shell
wpa_cli

scan
scan_results
add_network
set_network 0 ssid "<SSID>"
set_network 0 psk "<PSK>"
```

## Clone bootable SD card

### Create an SD card image

After the installation is done, SD card can be cloned:

```shell
diskutil list
```

Assumed, the SD-card is displayed as `/dev/disk4`

```shell
diskutil unmount /dev/disk4
sudo dd if=/dev/disk4 of=7c.img
docker run --privileged=true --rm \
    --volume $(pwd):/workdir \
    monsieurborges/pishrink \
    pishrink -aZv 7c.img 7c_shrinked.img
```

Eject the SD card.

### Copy the SD card image

Insert a new SD card.

```shell
sudo dd if=7c_shrinked.img of=/dev/disk4
```

## Install development environment

### Python

- Install Python 3.9
  - [Download](https://www.python.org/downloads/release/python-3916/)
  - [Mac: Homebrew](https://formulae.brew.sh/formula/python@3.9)
    - `brew install python@3.9`
  - Install python extensions:
    - `pip install Pillow`
    - `pip install requests`
    - `pip install python-dateutil`

### RGBMatrixEmulator

- Install RGBMatrixEmulator with `pip install RGBMatrixEmulator==0.10.0`
- Clone [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator)

Smoke-test with:

```shell
cd RGBMatrixEmulator/samples
python runtext.py
```

Open `http://localhost:8888` in browser, "Hello world!" is to be displayed.
