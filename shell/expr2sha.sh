#!/bin/bash
read -s -p "origin > " pwd
echo -ne "\nshasum > "
echo $pwd | bc | sha256sum
