#!/bin/bash

set -e
trap 'echo "Error: command failed at line $LINENO" >&2' ERR

usage() {
    echo "Usage: $0 SCRIPT_FILE PANEL_IP [SCRIPT_ARGS...]"
    echo ""
    echo "Execute a setup script on a remote panel via SSH."
    echo ""
    echo "Arguments:"
    echo "  SCRIPT_FILE   Path to the script file to execute on the panel"
    echo "  PANEL_IP      IP address of the target panel"
    echo "  SCRIPT_ARGS   Optional arguments forwarded to the remote script"
    echo ""
    echo "Examples:"
    echo "  $0 m1-setup/_setup.sh 192.168.1.100"
    echo "  $0 m1-setup/_setup.sh 192.168.1.100 dev/my-feature"
    echo "  $0 m1-setup/_setup.sh 192.168.1.100 dev https://dl.sevencourts.com/s/XXXXX/download"
    exit 1
}

# Show help if requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
fi

# Validate arguments
if [[ $# -lt 2 ]]; then
    echo "Error: Expected at least 2 arguments, got $#"
    usage
fi

SCRIPT_FILE=$1
PANEL_IP=$2
shift 2
SCRIPT_ARGS=("$@")

SSH_OPTS="-o StrictHostKeyChecking=no"

# Validate script file exists
if [[ ! -f "$SCRIPT_FILE" ]]; then
    echo "Error: Script file '$SCRIPT_FILE' not found"
    exit 1
fi

SCRIPT_DIR=$(dirname "$SCRIPT_FILE")
SCRIPT_NAME=$(basename "$SCRIPT_FILE")

set -x

if [[ "$SCRIPT_DIR" != "." ]]; then
    PACKAGE_NAME=$(basename "$SCRIPT_DIR")
    REMOTE_DIR="/tmp/$PACKAGE_NAME"
    scp $SSH_OPTS -r "$SCRIPT_DIR" "user@$PANEL_IP:/tmp/"
else
    REMOTE_DIR="/tmp"
    scp $SSH_OPTS "$SCRIPT_FILE" "user@$PANEL_IP:$REMOTE_DIR/$SCRIPT_NAME"
fi

ssh $SSH_OPTS "user@$PANEL_IP" chmod +x "$REMOTE_DIR/$SCRIPT_NAME"
# The remote script may reboot the panel, which closes the SSH connection
# and returns a non-zero exit code. Treat exit code 255 (SSH disconnect) as success.
ssh $SSH_OPTS "user@$PANEL_IP" sudo bash "$REMOTE_DIR/$SCRIPT_NAME" "${SCRIPT_ARGS[@]}" \
  || { rc=$?; [ $rc -eq 255 ] && echo "Panel rebooting — install complete." || exit $rc; }
