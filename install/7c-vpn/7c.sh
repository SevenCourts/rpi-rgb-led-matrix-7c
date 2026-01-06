#!/bin/bash

grep CLIENT_LIST,tableau-vpn-client /var/log/openvpn/openvpn-status.log | while read -r line ; do
    IFS=',' read -r -a values <<< "$line"
    IP="${values[3]}"
    echo $IP
    ssh -n -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o PasswordAuthentication=no root@"$IP" 'hostname'
    echo "---"
done