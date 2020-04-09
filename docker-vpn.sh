# All traffic coming from 127.18.0.0/24 should go through route table 10
ip rule add from 127.18.0.0/24 lookup 10
# Add necessary routes to route table 10
ip route add default dev tun0 table 10
ip route add 127.18.0.0/24 dev br-a70eb636fdcd table 10
# If you want to access the host's subnet as well from the docker network
ip route add 192.168.1.0/24 dev wlp2s0 table 10
