#!/bin/bash

m_error(){
    echo -e "usage:\t$0 [install [packages]...|remove]"
}
m_autoremove(){
    echo "run apt autoremove..."
    echo "----------------------------------------"
    echo "listing..."
    apt --dry-run autoremove 2>/dev/null | grep -Po '^Remv \K[^ ]+'
    if [[ $# -le 0 || $1 != "-y" ]]; then
        while true; do
            read -p "remove these?[y/n]" yn
            case $yn in
            y|Y)
                    sudo apt autoremove -y
                    break
                    ;;
            n|N)
                    exit 1
                    break
                    ;;
            *) 
                    echo "Please answer yes or no."
                    break
                    ;;
            esac
        done
    fi
    echo "removed"
    echo "----------------------------------------"    
}
m_install(){
    for i in "$@"; do
        exist_flag="false"
        flag="false"
        if [[ $(apt list $i 2>/dev/null | grep $i) != "" ]]; then
            exist_flag="true"
        fi
        if [[ $(apt list $i --installed 2>/dev/null | grep $i) != "" ]]; then
            flag="true"
        fi
        
        if [ $exist_flag == "true" ]; then
            if [ $flag == "false" ]; then
                echo -n "$i :"
                sudo apt install $i -y >/dev/null 2>/dev/null
                echo -n "installed"
                sudo apt-mark auto $i  >/dev/null 2>/dev/null
                echo ",marked auto."
            else
                echo "[warning]: $i already installed!" >&2
            fi
        else
            echo "[error]: $i not found!" >&2
        fi
    done
}

if [ $# -le 0 ]; then
    m_error
elif [ $1 == "install" ]; then
    if [ $# -le 1 ]; then
        m_error
    else
        args=$(echo $* | cut -d ' ' -f 2-)
        if [[ $# -ge 3 && $(echo $args | rev | cut -d ' ' -f 1 | rev) == "-y" ]]; then
            m_autoremove -y
            args=$(echo $args | rev | cut -d ' ' -f 2- | rev)
        else
            m_autoremove
        fi
        m_install $args
    fi
elif [ $1 == "remove" ]; then
    if [ $# -ne 1 ]; then
        m_error
    else
        m_autoremove
    fi
else
    m_error
fi
