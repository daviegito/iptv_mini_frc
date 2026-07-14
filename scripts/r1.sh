#!/bin/bash

sudo systemctl stop NetworkManager
sudo ifconfig enp0s8 172.16.0.1 netmask 255.255.255.0 up
sudo ifconfig ppp0 10.0.0.1 netmask 255.255.255.0 up

echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
sudo sysctl -w net.ipv4.ip_forward=1

sudo ip route add 192.168.0.0/24 via 10.0.0.2 dev ppp0

sudo sysctl -w net.ipv4.conf.all.rp_filter=0
sudo sysctl -w net.ipv4.conf.default.rp_filter=0

sudo ifconfig ppp0 multicast
sudo systemctl stop smcroute
sudo smcrouted

sudo smcroutectl join enp0s8 224.0.1.2
sudo smcroutectl add enp0s8 172.16.0.2 224.0.1.2 ppp0

ip a
ip route
sudo iptables -t nat -L -v -n
cat /proc/net/ip_mr_vif

# Regra de Ouro: Limitando a banda da interface WAN (ppp0) para 115200 bps
sudo tc qdisc add dev ppp0 root tbf rate 115200bit burst 10kb latency 50ms
