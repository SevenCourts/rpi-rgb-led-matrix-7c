import subprocess
import socket
import re
import platform
from urllib.parse import urlparse
import socket

import m1_logging

NETWORK_TIMEOUT_SECONDS = 4

# The host to check for general internet access:
INTERNET_CHECK_HOST_IP = "8.8.8.8"  # Google's public DNS server
INTERNET_CHECK_TIMEOUT_SECONDS = 3

SEVENCOURTS_PROD_SERVER_URL = "https://prod.server.sevencourts.com"

SEVENCOURTS_SERVER_TIMEOUT_SECONDS = 3
SHELL_COMMAND_EXECUTION_TIMEOUT_SECONDS = 5

logger = m1_logging.logger("network")

def ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((INTERNET_CHECK_HOST_IP, 80))
        result = s.getsockname()[0]
        s.close()
    except Exception as e:
        logger.exception(e)
        result = "###"
    return result


def _run_command(command):
    """
    Executes a shell command and returns its output.
    Handles potential errors during command execution.
    """
    try:
        # Use subprocess.run for more control over output and error handling
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,  # Decode stdout/stderr as text
            check=True, # Raise CalledProcessError if the command returns a non-zero exit code
            timeout=SHELL_COMMAND_EXECUTION_TIMEOUT_SECONDS
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command '{' '.join(command)}': {e}")
        logger.error(f"Stderr: {e.stderr.strip()}")
        return None
    except subprocess.TimeoutExpired:
        logger.error(f"Command '{' '.join(command)}' timed out.")
        return None
    except FileNotFoundError:
        logger.error(f"Command '{command[0]}' not found. Ensure it's installed and in the PATH.")
        return None

def get_active_interfaces():
    """
    Identifies active ("UP") network interfaces on the system.
    Parses the output of 'ip link show'.
    """
    interfaces = []
    # 'ip -o link show' provides one interface per line, easier to parse
    output = _run_command(["ip", "-o", "link", "show"])
    if output:
        # Regex to find interface name and 'state UP'
        # Example line: 1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000\    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
        # We are looking for lines containing 'state UP'
        for line in output.splitlines():
            match = re.search(r"^\d+:\s+(\S+):\s+<.*UP.*>", line)
            if match:
                interface_name = match.group(1)
                # Exclude loopback interface
                if interface_name != "lo":
                    interfaces.append(interface_name)
    return interfaces

def get_interface_type(interface_name):
    """
    Determines if an interface is LAN (Ethernet) or WLAN (Wireless).
    Checks for 'ether' or 'wlan' in the 'ip link show' output.
    """
    # For WLAN, 'iw' command is more reliable to confirm it's wireless
    # We'll assume if it's not 'ether' and often named 'wlanX', it's WLAN
    # A more robust check might involve 'iw dev <interface> info'
    if "wlan" in interface_name.lower(): # Common naming convention
        return "WLAN"
    else:
        output = _run_command(["ip", "link", "show", interface_name])
        if output:        
            if "link/ether" in output:
                return "LAN"
            elif "link/loopback" in output: # Should ideally be filtered out earlier
                return "Loopback"    
    return "Unknown"

def get_wlan_ssid(interface_name):
    """
    Retrieves the SSID (network name) for a WLAN interface.
    Uses 'iwgetid' command.
    """
    # iwgetid is usually available on Raspberry Pi for getting SSID
    output = _run_command(["iwgetid", interface_name, "--raw"])
    if output:
        # iwgetid --raw returns just the SSID
        return output.strip()
    return "Not connected or SSID not found"

def check_internet_access(host=INTERNET_CHECK_HOST_IP, timeout=INTERNET_CHECK_TIMEOUT_SECONDS):
    """
    Checks if there is general internet connectivity by attempting to
    connect to a well-known public host (e.g., Google DNS).
    """
    try:
        # Try to resolve the hostname and connect to a common port (e.g., 53 for DNS)
        # This is more reliable than ping as ICMP (ping) might be blocked.
        socket.setdefaulttimeout(timeout)
        socket.create_connection((host, 53)) # Port 53 for DNS
        return True
    except socket.error as e:
        logger.error(f"Internet check failed ({host}): {e}")
        return False
    except socket.timeout:
        logger.error(f"Internet check timed out ({host}).")
        return False
    
def _get_port_and_address(url_string):
    """
    Extracts the hostname (address) and port from a URL string.
    Returns default ports if a port is not explicitly specified.
    """
    parsed_url = urlparse(url_string)
    
    # Get the hostname (address)
    address = parsed_url.hostname
    
    # Get the port
    port = parsed_url.port
    
    # If the port is None, use the default port based on the scheme
    if port is None:
        if parsed_url.scheme == 'https':
            port = 443
        elif parsed_url.scheme == 'http':
            port = 80        
        
    return address, port

def check_server_access(server_url, timeout=SEVENCOURTS_SERVER_TIMEOUT_SECONDS):
    """
    Checks if a specific server is accessible by attempting a TCP connection
    to a specified port.
    """
    try:        
        server_address, port = _get_port_and_address(server_url)
        # Resolve the server address to an IP
        ip_address = socket.gethostbyname(server_address)
        sock = socket.create_connection((ip_address, port), timeout)
        sock.close()
        return True
    except socket.gaierror:
        logger.error(f"Could not resolve server address: {server_address}")
        return False
    except socket.error as e:
        logger.error(f"Server access check failed ({server_address}:{port}): {e}")
        return False
    except socket.timeout:
        logger.error(f"Server access check timed out ({server_address}:{port}).")
        return False

def main(server_url=SEVENCOURTS_PROD_SERVER_URL):
    """
    Main function to orchestrate the network information gathering.
    """
    logger.debug("1. Checking Network Interface Status")

    active_interfaces = get_active_interfaces()

    if not active_interfaces:
        logger.warning("No active network interfaces found (excluding loopback).")
    else:
        for iface in active_interfaces:
            logger.info(f"Interface: {iface} is on: Yes (Detected as UP)")

            iface_type = get_interface_type(iface)
            logger.info(f"Interface: {iface} type: {iface_type}")

            if iface_type == "WLAN":
                ssid = get_wlan_ssid(iface)
                logger.info(f"Interface: {iface} WLAN Name (SSID): {ssid}")
            else:
                logger.warning(f"Interface: {iface} WLAN Name (SSID): N/A (Not a WLAN interface)")

    logger.debug("2. Checking Internet and Server Accessibility")

    if check_internet_access():
        logger.info(f"Internet is accessible (via {INTERNET_CHECK_HOST_IP})")

        if check_server_access(server_url):
            logger.info(f"SevenCourts server is accessible: {server_url}")
        else:
            logger.warning(f"SevenCourts server in NOT accessible: {server_url}")
    else:
        logger.warning(f"Internet is NOT accessible")
        logger.warning(f"Cannot check SevenCourts server accessibility: Internet not accessible.")

if __name__ == "__main__":
    # Ensure the script is run with root privileges if necessary for some commands
    # (e.g., 'iwgetid' might require it on some setups, though often not)
    if platform.system() == "Linux" and subprocess.run(["id", "-u"], capture_output=True, text=True).stdout.strip() != "0":
        print("Warning: Some commands (e.g., iwgetid) might require root privileges.")
        print("Consider running this script with 'sudo python3 your_script_name.py'")
    main()