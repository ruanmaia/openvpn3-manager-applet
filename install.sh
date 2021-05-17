#!/bin/bash

export SUDO_USER_HOME=$(eval echo ~${SUDO_USER})

apt install libappindicator3-dev python3 python3-gi openvpn3 -y --no-install-recommends

mkdir -p /usr/share/applications /usr/share/openvpn3-manager-applet

cp ./usr/bin/openvpn3-manager-applet /usr/bin/openvpn3-manager-applet
cp ./usr/share/applications/openvpn3-manager-applet.desktop /usr/share/applications/openvpn3-manager-applet.desktop
cp ./usr/share/openvpn3-manager-applet/application_logo.png /usr/share/openvpn3-manager-applet/application_logo.png
cp ./usr/share/openvpn3-manager-applet/run.py /usr/share/openvpn3-manager-applet/run.py

update-desktop-database

mkdir -p $SUDO_USER_HOME/.vpn
mkdir -p $SUDO_USER_HOME/.config/openvpn3-manager-applet