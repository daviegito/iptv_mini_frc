# Guia de Configuração Manual (Simulando o Laboratório)

Como configuramos o `Vagrantfile` para NÃO definir IPs automaticamente, ao subir as máquinas (`vagrant up`), elas terão as placas de rede conectadas aos "cabos" (redes lan1, wan, lan2), mas sem os endereços IP. 
O seu trabalho (para praticar) é entrar em cada máquina e rodar os comandos abaixo como root.

## 1. Configurando IPs

### Na máquina R1 (`vagrant ssh r1`)
```bash
sudo su
# Configura o IP da porta ligada na LAN1
ip addr add 172.16.0.1/16 dev eth1
ip link set eth1 up

# Configura o IP da porta ligada no enlace WAN
ip addr add 10.0.0.1/30 dev eth2
ip link set eth2 up
```

### Na máquina R2 (`vagrant ssh r2`)
```bash
sudo su
# Configura o IP da porta ligada no enlace WAN
ip addr add 10.0.0.2/30 dev eth1
ip link set eth1 up

# Configura o IP da porta ligada na LAN2 (onde ficam os clientes lentos X e Y)
ip addr add 192.168.0.1/24 dev eth2
ip link set eth2 up
```

### Na máquina S (Servidor) (`vagrant ssh s`)
```bash
sudo su
# Configura o IP da LAN1
ip addr add 172.16.0.2/16 dev eth1
ip link set eth1 up

# Diz para o servidor que a saída para a internet/outras redes é pelo R1
ip route add default via 172.16.0.1
```

## 2. Roteamento Multicast (Exemplo Simplificado)
Para que os vídeos em Multicast (IPs `239.x.x.x`) passem pelos roteadores R1 e R2, você precisará habilitar o roteamento multicast no kernel e, dependendo do linux, rodar um daemon de roteamento (como o `pimd` ou usar rotas estáticas `smcroute`).
```bash
# Em R1 e R2 (habilita roteamento IP no kernel)
echo 1 > /proc/sys/net/ipv4/ip_forward
echo 1 > /proc/sys/net/ipv4/conf/all/mc_forwarding
```

## 3. Controle de Banda (Traffic Control) no Enlace WAN
No roteador **R1**, na placa que vai para R2 (eth2), limitamos a banda usando a ferramenta `tc`:
```bash
# Limita a saída da eth2 para 115200 bps
tc qdisc add dev eth2 root tbf rate 115200bit burst 10kb latency 50ms
```

## 4. NAT (Source NAT) no R1
O roteador R1 precisa fazer Source NAT (Masquerade) para que os pacotes que vêm de S (172.16.0.2) mascarados ganhem acesso à rede externa (que neste caso simulado do Vagrant é a eth0).
```bash
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```
