#!/bin/bash

while getopts v: flag
do
    case "${flag}" in
        v) vpn=${OPTARG};;

    esac
done

if [ ! -z "$vpn" ]
then
  echo "Connecting to VPN $vpn"
  networksetup -connectpppoeservice "$vpn"
  sleep 2
fi


python3 get_caseref.py

if [ ! -z "$vpn" ]
then
  echo "Disconnecting from VPN $vpn"
fi


aws-vault exec identity -- python -m pytest -n2 --dist=loadfile --html=report.html --self-contained-html
