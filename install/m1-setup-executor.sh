#!/bin/bash

set -ex

PANEL_IP=$1

sshpass -p "password" scp -o StrictHostKeyChecking=no -r 7c-os user@$PANEL_IP:/tmp/
sshpass -p "password" scp -o StrictHostKeyChecking=no -r 7c-vpn user@$PANEL_IP:/tmp/

SCRIPT=_m1_setup.sh
# SCRIPT=_m1_update_vpn.sh

sshpass -p "password" scp -o StrictHostKeyChecking=no $SCRIPT user@$PANEL_IP:/tmp/$SCRIPT
sshpass -p "password" ssh -o StrictHostKeyChecking=no user@$PANEL_IP chmod +x /tmp/$SCRIPT
sshpass -p "password" ssh -o StrictHostKeyChecking=no user@$PANEL_IP sudo bash /tmp/$SCRIPT
