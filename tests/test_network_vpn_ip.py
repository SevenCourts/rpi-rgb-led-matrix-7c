"""Unit tests for sevencourts.network.vpn_ip_address.

The tunnel address is read via ioctl(SIOCGIFADDR) on tun0; the ioctl is mocked
here so the tests run without a VPN (or without Linux at all).

Run with: python -m unittest tests.test_network_vpn_ip
(or via pytest if installed)
"""

import os
import socket
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sevencourts import network  # noqa: E402


def _ifreq_with_addr(name, addr):
    """Build the 256-byte buffer ioctl(SIOCGIFADDR) hands back for `addr`."""
    buf = bytearray(256)
    buf[: len(name)] = name.encode("utf-8")
    buf[16:18] = socket.AF_INET.to_bytes(2, "little")
    buf[20:24] = socket.inet_aton(addr)
    return bytes(buf)


class VpnIpAddressTest(unittest.TestCase):
    def test_address_present(self):
        with patch(
            "fcntl.ioctl", return_value=_ifreq_with_addr("tun0", "10.8.1.42")
        ) as ioctl:
            self.assertEqual(network.vpn_ip_address("tun0"), "10.8.1.42")
        self.assertEqual(ioctl.call_args[0][1], network.SIOCGIFADDR)
        self.assertTrue(ioctl.call_args[0][2].startswith(b"tun0\x00"))

    def test_interface_missing_returns_none(self):
        with patch("fcntl.ioctl", side_effect=OSError(19, "No such device")):
            self.assertIsNone(network.vpn_ip_address("tun0"))

    def test_interface_without_address_returns_none(self):
        # Interface exists but has no IPv4 address: EADDRNOTAVAIL.
        with patch(
            "fcntl.ioctl", side_effect=OSError(99, "Cannot assign requested address")
        ):
            self.assertIsNone(network.vpn_ip_address("tun0"))

    def test_defaults_to_vpn_interface_constant(self):
        with patch.object(network, "VPN_INTERFACE", "tun7"), patch(
            "fcntl.ioctl", return_value=_ifreq_with_addr("tun7", "10.8.1.7")
        ) as ioctl:
            self.assertEqual(network.vpn_ip_address(), "10.8.1.7")
        self.assertTrue(ioctl.call_args[0][2].startswith(b"tun7\x00"))


if __name__ == "__main__":
    unittest.main()
