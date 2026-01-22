#!/bin/bash

set -e

usage() {
    echo "Usage: $0 SCRIPT_FILE PANEL_IP"
    echo ""
    echo "Execute a setup script on a remote panel via SSH."
    echo ""
    echo "Arguments:"
    echo "  SCRIPT_FILE  Path to the script file to execute on the panel"
    echo "  PANEL_IP     IP address of the target panel"
    echo ""
    echo "Example:"
    echo "  $0 _m1_setup.sh 192.168.1.100"
    exit 1
}

# Show help if requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
fi

# Validate arguments
if [[ $# -ne 2 ]]; then
    echo "Error: Expected 2 arguments, got $#"
    usage
fi

SCRIPT_FILE=$1
PANEL_IP=$2

# Validate script file exists
if [[ ! -f "$SCRIPT_FILE" ]]; then
    echo "Error: Script file '$SCRIPT_FILE' not found"
    exit 1
fi

set -x

SCRIPT_NAME=$(basename "$SCRIPT_FILE")

# Copy dependencies needed only for _m1_setup.sh
if [[ "$SCRIPT_NAME" == "_m1_setup.sh" ]]; then
    scp -o StrictHostKeyChecking=no -r 7c-os $PANEL_IP:/tmp/
    scp -o StrictHostKeyChecking=no -r 7c-vpn $PANEL_IP:/tmp/
fi

scp -o StrictHostKeyChecking=no "$SCRIPT_FILE" $PANEL_IP:/tmp/$SCRIPT_NAME
ssh -o StrictHostKeyChecking=no $PANEL_IP chmod +x /tmp/$SCRIPT_NAME
ssh -o StrictHostKeyChecking=no $PANEL_IP sudo bash /tmp/$SCRIPT_NAME