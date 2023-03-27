# 7C-M1 set-up

## Install firmware

### OS & dev tools


- Install [Raspberry PI OS Lite 64 bit](https://www.raspberypi.com/documentation/computers/getting-started.html#installing-the-operating-system)

- Insert the SD card to Raspi and boot
- **FIXME**: Set login: "user" and pasword: "password"  

- Find out the IP address of the Raspi
    - For SUPREMATIC Mikrotik router: http://192.168.114.1/webfig/#IP:DHCP_Server.Leases
    - Or use any IP scanner available
- Turn on ssh:
    - Enter `sudo raspi-config` in a terminal window.
    - Select Interfacing Options.
    - Navigate to and select SSH.
    - Choose Yes.

- Log in with `ssh user@<ip-address>` (password: `password`)
- Change timezone to Europe/Berlin via `raspi-config` / Localization. **FIXME**: do it via shell.

### Install dependencies

```
sudo -i
apt update
apt install git vim build-essential
```

### Set hostname

Define PANEL_NAME (the last 8 digits of the serial number):

```
cat /sys/firmware/devicetree/base/serial-number | tail -c +9
```
Set the hostname via `raspi-config` manually. **FIXME**: do it via `7c-hostname.service`

      
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
sudo apt-get update --allow-releaseinfo-change && sudo apt-get install python3-dev python3-pillow python3-requests -y
make build-python PYTHON=$(command -v python3)
sudo make install-python PYTHON=$(command -v python3)
```

### Install rpi-rgb-led-matrix-7c

TODO: check if we need to keep the directory structure?

```shell
cd /opt/7c/rpi-rgb-led-matrix/bindings/python
git clone https://bitbucket.org/suprematic/rpi-rgb-led-matrix-7c.git
```


### Run smoke-test (Failed)

```shell
cd /opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c
./m1.sh
```

The panel should display current time.

## Set up 7c systemd service

```shell
cp etc/systemd/system/7c.service /etc/systemd/system/7c.service
cp etc/systemd/system/7c-demo.service /etc/systemd/system/7c-demo.service
```

Service start:
```shell
systemctl start 7c.service
```

Service auto-start:
```shell
systemctl enable 7c.service
```

## Install 7c-controller

```
curl -o /opt/7c/7c_m1_controller https://dl.suprematic.net/index.php/s/YHWrGCaJ42XTpdx/download
chmod u+x /opt/7c/7c_m1_controller
cp etc/systemd/system/7c-controller.service /etc/systemd/system/7c-controller.service
systemd enable 7c-controller
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

### Check the log:

```
journalctl -e -u openvpn-client@callhome
journalctl -f -u openvpn-client@callhome
```

### Test: connect to the panel via SSH

- Login to `7c-vpn.suprematic.team` via SSH using personal LDAP credentials

```
sudo -i
./7c.sh
```

Should display the list of scoreboards: hostnames together with their respective IP addresses as they are accessible from the 7c-vpn server.

```
10.8.0.4
7C-M1-R2
---
10.8.0.2
7C-M1-R3
---
```

Connect to chosen scoreboard via SSH from `7c-vpn.suprematic.team`:

```
ssh 10.8.0.4
```


## Final test


Disconnect from Ethernet, reboot.

=> The panel should display current time and the blue dot.


### Test WiFi setting

- Open SevenCourts Admin iOS app
- Connect the panel to "SUPREMATIC_INTERNAL" network

=> The panel should display current time only.

Reboot. The panel should display:

=> ~15 seconds of black screen
=> ~5 second current time and the blue dot
=> current time only


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

- Install RGBMatrixEmulator with `pip install RGBMatrixEmulator`
- Clone [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator)

Smoke-test with:
```
cd RGBMatrixEmulator/samples
python runtext.py
```

Open `http://localhost:8888` in browser, "Hello world!" is to be displayed.
