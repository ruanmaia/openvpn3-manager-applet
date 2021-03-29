# OpenVPN 3.0 Manager Applet

## 1. Install the `openvpn3` client packages
Follows this instructions:


[https://openvpn.net/cloud-docs/openvpn-3-client-for-linux/](https://openvpn.net/cloud-docs/openvpn-3-client-for-linux/)

## 2. Download and install the `openvpn3-manager-applet-v1.0.1.deb`
```shell
$ wget https://github.com/ruanmaia/openvpn3-manager-applet/raw/master/openvpn3-manager-applet-v1.0.1.deb

$ apt install ./openvpn3-manager-applet-v1.0.1.deb 
```
## 3. Initialize the OpenVPN 3.0 Manager Applet
Open your application menu and type `openvpn3`


## 4. Add the `.ovpn` files to your `~/.vpn` folder
```shell
$ pwd
/home/rmaia/

$ cd .vpn && ll
total 12K
-rw-rw-r-- 1 rmaia rmaia 1,9K mar 28 20:07 aws-app-dev.ovpn
-rw-rw-r-- 1 rmaia rmaia 1,9K mar 28 20:06 aws-app-prod.ovpn
```
## 5. Update your VPN configuration
> Note that are a new file on your `~/.vpn` folder:
```shell
-rw-rw-r-- 1 rmaia rmaia   61 mar 29 07:31 credentials.db
```
This file will store your credentials. When you try to connect on a VPN for the first time, a dialog will popup on your screen. It will ask for the username and password. 

In the next connection you **DO NOT** will be asked anymore! =)

## 6. If you add or remove an `.ovpn` files, just remember to reload the OpenVPN 3.0 Manager Applet
Click on the `lock applet icon`, then choose *"Update Config Files"* option.


# Enjoy!