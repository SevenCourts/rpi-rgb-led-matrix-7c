# 7c-vpn.sevencourts.com

## Hetzner console

Open [Hetzner cloud panel](https://console.hetzner.cloud/projects/10223230/dashboard).

With `admins@sevencourts.com` user

All servers:
<https://console.hetzner.com/projects/10223230/servers>

Select `node1-vpn-clone`:
<https://console.hetzner.com/projects/10223230/servers/102403060/overview>

## Issue with the expired certificate

Symptoms:

1. `ssh 7c-vpn.sevencourts.com` does not work.
2. In the console prompt there is "time-journal ... rotating" text.s

## How to reboot server

- Login to Hetzner web console.
- Turn the server OFF.
- Turn the server ON.
- Check in the Hetzner console prompt that server is started.

Login via ssh `ssh 7c-vpn.sevencourts.com`, then with `root` user:

```bash
timedatectl set-time 2025-05-01
systemctl restart openvpn-server@sevencourts.service
journalctl -xeu openvpn-server@sevencourts.service -f
```

Wait about 5-10 minutes for the clients to be connected.
