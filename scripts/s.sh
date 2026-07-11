#!/bin/bash

sudo systemctl stop NetworkManager
sudo ifconfig enp0s8 172.16.0.2 netmask 255.255.255.0 up
sudo route add -net 224.0.0.0 netmask 240.0.0.0 dev enp0s8
sudo route add -net 192.168.0.0 netmask 255.255.255.0 gw 172.16.0.1
ip a
ip route
ping -c 3 172.16.0.1
