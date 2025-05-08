#!/bin/bash

set -ex

PANEL_IP=$1

SCRIPT=m1-install.sh
sshpass -p "password" scp $SCRIPT $PANEL_IP:/tmp/$SCRIPT
sshpass -p "password" ssh $PANEL_IP chmod +x /tmp/$SCRIPT
sshpass -p "password" ssh $PANEL_IP sudo /tmp/$SCRIPT
