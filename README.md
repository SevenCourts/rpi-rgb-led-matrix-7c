# 7C-M1 set-up

## Install firmware

### OS & dev tools

- Install [Raspberry PI OS Lite 64 bit](https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system) ver. 5.15.84-v8+ 
    - Use exactly this version of RaspiOS: https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2023-02-22/    
- Insert the SD card to Raspi, connect monitor, keyboard, ethernet
- On the first boot: set login: "user" and password: "password" 
    - **FIXME** define non-default login/password
- Turn on ssh:
    - Enter `sudo raspi-config` in a terminal window
    - Select "Interface Options"
    - Navigate to and select "SSH"
    - Choose "Yes"

The rest can be done via SSH:
    
- Find out the IP address of the Raspi
    - e.g. with SUPREMATIC Mikrotik router: http://192.168.114.1/webfig/#IP:DHCP_Server.Leases
    - or use any IP scanner software

- Log in with `ssh user@<ip-address>` (password: `password`)

- Open sudo session with `sudo -i`


### Set the country code (must do to enable WiFi)

Find your country's code here: https://en.wikipedia.org/wiki/ISO_3166-1

```
raspi-config nonint do_wifi_country DE
```

or (Derek)

```
raspi-config nonint do_wifi_country US
```


### Change timezone

```
timedatectl set-timezone Europe/Berlin
```

or (Derek)

```
timedatectl set-timezone US/Eastern
```

### Install dependencies

```
apt update
apt install git vim build-essential -y
```

### Install and make rpi-rgb-led-matrix SDK

```shell
mkdir /opt/7c
cd /opt/7c
git clone https://github.com/suprematic/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix/
git checkout 7c/m1/dev
make
```

### Install and make python3 bindings

```shell
sudo apt-get update --allow-releaseinfo-change && sudo apt-get install python3-dev python3-pillow python3-requests python3-gpiozero -y
make build-python PYTHON=$(command -v python3)
sudo make install-python PYTHON=$(command -v python3)
```

### Install rpi-rgb-led-matrix-7c

TODO: check if we need to keep the directory structure?

```shell
cd /opt/7c/rpi-rgb-led-matrix/bindings/python
git clone https://bitbucket.org/suprematic/rpi-rgb-led-matrix-7c.git
```

### Turn off sound card

```
echo "blacklist snd_bcm2835" >> /etc/modprobe.d/alsa-blacklist.conf
```

### Set up 7c hostname systemd service

```
cd /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c
cp opt/7c/7c-set-hostname.sh /opt/7c/7c-set-hostname.sh
chmod u+x /opt/7c/7c-set-hostname.sh
cp etc/systemd/system/7c-hostname.service /etc/systemd/system/7c-hostname.service
systemctl enable 7c-hostname
```


## Set up 7c systemd services

```shell
cp etc/systemd/system/7c.service /etc/systemd/system/7c.service
cp etc/systemd/system/7c-demo.service /etc/systemd/system/7c-demo.service
```

Enable service and start now:

```shell
systemctl enable --now 7c.service
```

## Install 7c-controller

```
cd /opt/7c
curl -o 7c_m1_controller.zip https://dl.suprematic.net/index.php/s/YHWrGCaJ42XTpdx/download
unzip 7c_m1_controller.zip
chmod u+x 7c_m1_controller

cd /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c
cp etc/systemd/system/7c-controller.service /etc/systemd/system/7c-controller.service
systemctl enable 7c-controller
```


## Install 'Call Home' VPN

Full documentation: see the [Wiki page](https://wiki.suprematic.team/books/tennis-cast-scoreboard/page/call-home-vpn-for-7c-scoreboard).

```
apt-get install openvpn -y
mkdir -p /root/.ssh/
cp 7c-vpn/ssh/authorized_keys /root/.ssh/authorized_keys
cp 7c-vpn/etc/openvpn/client/callhome.conf /etc/openvpn/client/callhome.conf
mkdir -p /etc/systemd/system/openvpn-client@callhome.service.d/
cp 7c-vpn/etc/systemd/system/openvpn-client@callhome.service.d/override.conf /etc/systemd/system/openvpn-client@callhome.service.d/override.conf
systemctl daemon-reload
systemctl enable --now openvpn-client@callhome
```



## Tests

The board is connected to Ethernet.


```shell
reboot
```

=> The panel should display some time (may be different from current) and the blue dot.


```shell
ssh user@<ip-address>
sudo -i
```

### Validate and register the hostname:

```shell
hostname
```
Should output the last 8 bytes of `/sys/firmware/devicetree/base/serial-number` file contents.

Insert the hostname into the "Hostname" column of https://docs.google.com/spreadsheets/d/1ewMfZ9fwiHdyakF1-PI1sjMTP-t4OwbRadxDGT6VGtM/edit#gid=696316085 spreadsheet.


### Check the 'Call home VPN' log:

```shell
journalctl -e -u openvpn-client@callhome
journalctl -f -u openvpn-client@callhome
```

### Connect to the panel via "Call home VPN" server

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

Connect to the chosen scoreboard via SSH from `7c-vpn.suprematic.team`:

```shell
ssh 10.8.0.4
```

### Final test

Disconnect from Ethernet, reboot.

=> The panel should display current time and the blue dot.


### Test WiFi setting

- Open "SevenCourts Admin" iOS app
- Connect the panel to a WiFi network (e.g. SUPREMATIC_INTERNAL)

=> The panel should display current time and no blue dot.

Reboot. The panel should display:

=> ~15 seconds of black screen
=> ~5 second current time and the blue dot
=> current time only


## Update Firmware

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

- https://forums.raspberrypi.com/viewtopic.php?t=21632
- https://loganmarchione.com/2021/07/raspi-configs-mostly-undocumented-non-interactive-mode/

```shell
wpa_cli

scan
scan_results
add_network
set_network 0 ssid "<SSID>"
set_network 0 psk "<PSK>"
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

### RGBMatrixEmulator

- Install RGBMatrixEmulator with `pip install RGBMatrixEmulator==0.10.0`
- Clone [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator)

Smoke-test with:
```
cd RGBMatrixEmulator/samples
python runtext.py
```

Open `http://localhost:8888` in browser, "Hello world!" is to be displayed.
