#!/bin/bash

check_internet() {
    ping -c 5 -i 0.2 -w 5 114.114.114.114 >/dev/null
}

getip() {
    CURRENT_IP=$(upnpc -s | grep ExternalIPAddress | head -n 1 | grep -oE "10.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}")
}

tdxy_login() {
    echo "[$(date +"%Y-%m-%d-%H:%M:%S")] try to login.."
    getip
    echo "[$(date +"%Y-%m-%d-%H:%M:%S")] ip:$CURRENT_IP"
    LOGIN_STATUS=$(curl -s "http://10.255.255.11:801/eportal/?c=Portal&a=login&login_method=1&user_account=$username%40$operator&user_password=$password&wlan_user_ip=$CURRENT_IP" -H 'Connection: keep-alive' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36' -H 'DNT: 1' -H 'Accept: */*' -H 'Referer: http://10.255.255.11/' -H 'Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-MO;q=0.6,ja-JP;q=0.5,ja;q=0.4' --compressed --insecure)
    echo -e "[$(date +"%Y-%m-%d-%H:%M:%S")] login result:$LOGIN_STATUS"
}

usage() {
    echo -e "Usage: $0 OPTION" 1>&2
    echo -e "  -u\t username" 1>&2
    echo -e "  -p\t password" 1>&2
    echo -e "  -o\t operator (telecom, unicom, cmcc)" 1>&2
    echo -e "  -c\t config file (username, password, operator separated by space)" 1>&2
    exit 1
}

while getopts ":u:p:o:c:" o; do
    case "$o" in
    u)
        username=$OPTARG
        ;;
    p)
        password=$OPTARG
        ;;
    o)
        operator=$OPTARG
        ;;
    c)
        config=$OPTARG
        ;;
    esac
done
shift $((OPTIND - 1))
if [[ -n $config && -f $config ]]; then
    cnt=$(($(cat $config | grep -o " " | wc -l) + 1))
    if [[ $cnt -eq 3 ]]; then
        username=$(cat $config | cut -d ' ' -f 1)
        password=$(cat $config | cut -d ' ' -f 2)
        operator=$(cat $config | cut -d ' ' -f 3)
    fi
fi
if [[ -z $username || -z $password || -z $operator ]]; then
    usage
fi

while true; do
    check_internet
    res=$?
    until [[ $res -eq 0 ]]; do
        tdxy_login $1
        check_internet
        res=$?
    done
    echo "[$(date +"%Y-%m-%d-%H:%M:%S")] logged in"
    sleep 30s
done
exit 0
