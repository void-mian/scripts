#!/bin/bash

check_internet() {
    ping -c 5 -i 0.2 -w 5 114.114.114.114 >/dev/null
}

tdxy_logout() {
    echo "[$(date +"%Y-%m-%d-%H:%M:%S")] try to logout.."
    LOGOUT_STATUS=$(curl -s 'http://10.255.255.11:801/eportal/?c=Portal&a=logout')
    echo -e "[$(date +"%Y-%m-%d-%H:%M:%S")] logout result:$LOGOUT_STATUS"
}

check_internet
res=$?
until [[ $res -ne 0 ]]; do
    tdxy_logout
    check_internet
    res=$?
done
echo "[$(date +"%Y-%m-%d-%H:%M:%S")] logged out"
exit 0
