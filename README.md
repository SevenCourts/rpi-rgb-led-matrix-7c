# 7C-M1 set-up

Use Ethernet for initial set-up.

## Pre-requisites

Define PANEL_NAME (the last 8 digits of the serial number):

```
cat /sys/firmware/devicetree/base/serial-number | tail -c +9

```

Set the hostname via `raspi-config`.

**FIXME**: do it via `7c-hostname.service`


## Install firmware

### OS & dev tools (DietPI, the subject to change)

- Install [DietPI](https://dietpi.com/docs/install/)

- Copy (overwrite) the prepared `dietpi/dietpi.txt` to the SD card
    - change `AUTO_SETUP_NET_HOSTNAME` to PANEL_NAME
- Setup WiFi credentials in `dietpi-wifi.txt`

- Insert the SD card to Raspi and boot

- Find out the IP address of the Raspi
    - For SUPREMATIC Mikrotik router: http://192.168.114.1/webfig/#IP:DHCP_Server.Leases
    - Or use any IP scanner available

- Log in with `ssh root@<ip-address>`
    - (The first boot will take some time)
    - Leave `dietpi` software password    
    - Disable the UART serial console in the dialog
    - `dietpi-software` dialog starts, search and install (same can be done with `apt`):
      - `git`
      - `vim`
      - `build-essential`
      
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


### Run smoke-test

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

## Install 7c-controller

```
curl -o /opt/7c/7c_m1_controller https://dl.suprematic.net/index.php/s/YHWrGCaJ42XTpdx
chmod u+x /opt/7c/7c_m1_controller
cp etc/systemd/system/7c-controller.service /etc/systemd/system/7c-controller.service
systemd enable 7c-controller
```


## Final test

```shell
reboot
```

The panel should display current time.


## Change WiFi to customer network

- Get WiFi SSID and key
- In `dietpi-config`:
    - Go to "7: Network Options: Adapters"
    - Go to "WiFi"
    - Go to "Scan"
    - Select "SUPREMATIC_INTERNAL" and remove it
    - Select the 0th slot
    - Select "Manual"
        - Enter SSID
        - Enter key
    - done, back, back, exit, ok


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
