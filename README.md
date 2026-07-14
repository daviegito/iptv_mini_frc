# Mini-IPTV Multicast com Controle de Banda (FRC)

Projeto universitário focado na construção de uma arquitetura completa de redes de computadores, unindo infraestrutura (Roteamento, Multicast, QoS/TC, Proxy Reverso) e desenvolvimento de software (API RESTful, JWT, Web Frontend).

## Arquitetura do Sistema

O projeto é dividido em três grandes blocos:
1. **Frontend (`/frontend`)**: Interface web construída em HTML5, CSS3 (Glassmorphism) e Vanilla Javascript. Responsável por consumir a API e disparar o VLC via download dinâmico de playlists `.m3u`.
2. **Backend (`/backend`)**: API desenvolvida em Python (FastAPI). Responsável pela autenticação segura de usuários (JWT), banco de dados (SQLite) e orquestração do FFmpeg para transmissão de streams de vídeo UDP (Multicast).
3. **Infraestrutura (`/infra` e `Vagrantfile`)**: Topologia de rede simulada com máquinas virtuais gerenciadas pelo Vagrant (hypervisor Libvirt/KVM). Contém a planta dos roteadores, clientes e configurações do Apache.

## Modos de Execucao

Existem duas formas de rodar o projeto: durante o desenvolvimento simulado (Vagrant) e o "valendo" no dia da apresentacao com a rede fisica.

### 1. Modo Desenvolvimento (Simulacao via Vagrant)
Este modo serve para a equipe testar o codigo e as regras de rede antes do dia da apresentacao. Toda a topologia e simulada usando Maquinas Virtuais no seu computador.

**Passos:**
1. Suba as maquinas com o acelerador KVM ativado: `sg kvm -c "vagrant up --no-parallel"`.
   *(Se a maquina travar no "Booting from Hard Disk", garanta que seu usuario faz parte dos grupos libvirt/kvm e que a pasta `/home/usuario` tem permissao de execucao `chmod +x`)*
2. Como a box genérica do Linux não monta pastas automaticamente, envie os arquivos do projeto para as VMs:
   - `vagrant upload backend/ backend/ s`
   - `vagrant upload frontend/ frontend/ r1`
   - `vagrant upload infra/ infra/ r1`
3. No terminal do Servidor (`vagrant ssh s`): Instale o `ffmpeg` e o Python, entre na pasta `~/backend` e ligue o servidor com `uvicorn main:app --host 0.0.0.0 --port 8000`.
4. No terminal do R1 (`vagrant ssh r1`): Configure o Apache, Proxy Reverso, Roteamento e QoS com os comandos:
   ```bash
   sudo apt update && sudo apt install apache2 -y
   sudo a2enmod proxy proxy_http rewrite
   sudo cp -r ~/frontend/* /var/www/html/
   sudo cp ~/infra/apache_proxy.conf /etc/apache2/sites-available/000-default.conf
   sudo systemctl restart apache2
   sudo sysctl -w net.ipv4.ip_forward=1
   sudo sysctl -w net.ipv4.conf.all.mc_forwarding=1
   sudo ip route add 192.168.0.0/24 via 10.0.0.253 dev eth2
   sudo tc qdisc add dev eth2 root tbf rate 115200bit burst 10kb latency 50ms
   ```
5. No terminal do R2 (`vagrant ssh r2`): Habilite o Roteamento Multicast e a rota estática inversa:
   ```bash
   sudo sysctl -w net.ipv4.ip_forward=1
   sudo sysctl -w net.ipv4.conf.all.mc_forwarding=1
   sudo ip route add 172.16.0.0/24 via 10.0.0.254 dev eth1
   ```
6. Nos terminais Clientes X e Y (`vagrant ssh x` ou `y`): Teste o recebimento dos pacotes de Video UDP Multicast escutando a rede com o tcpdump: `sudo tcpdump -i eth2 -n udp`

---

### 2. Modo Laboratorio (Apresentacao Fisica)
Neste modo, computadores reais (notebooks dos alunos) assumirao os papeis do diagrama (S, R1, R2, X, Y), conectados fisicamente por cabos de rede e switches.

**Passo 1: Topologia Fisica (Cabos)**
- Conecte o Notebook Servidor (S) e a porta LAN do Notebook R1 em um switch (Formando a rede LAN1).
- Conecte a porta WAN do Notebook R1 diretamente na porta WAN do Notebook R2 (Formando o gargalo da rede WAN).
- Conecte a porta LAN do Notebook R2 e os Notebooks Clientes (X, Y) em outro switch (Formando a rede LAN2).

**Passo 2: Configurar Roteadores (Notebooks Linux R1 e R2)**
- Configure as placas de rede fisicas de R1 e R2 com IPs compativeis com o diagrama do PDF.
- No Notebook R1, instale o Apache, hospede a pasta `/frontend` nele e ative o modulo de proxy (`a2enmod proxy_http`), repassando o trafego web para o IP fisico do Notebook S.
- Configure as rotas Multicast (PIM/IGMP), DHCP para os clientes e aplique a limitacao de banda de 115kbps (`tc`) na placa WAN do R2.

**Passo 3: Configurar Servidor (Notebook S)**
- Certifique-se de ter Python e o pacote `ffmpeg` instalados fisicamente.
- Navegue ate a pasta do `backend` e rode: `uvicorn main:app --host 0.0.0.0 --port 8000`.

**Passo 4: A Grande Apresentacao (Notebooks Clientes X e Y)**
- Nos notebooks clientes, abra o navegador e digite o IP fisico do Notebook R1.
- Faca o Login (ex: `hostx`), o proxy repassara a autenticacao para o Servidor S.
- Ao clicar em "Assistir", a aplicacao gerara o arquivo `.m3u` dinamicamente. Abra-o com o VLC!
- Prove ao professor que o segundo cliente a tentar assistir levara um Erro 429 devido a regra matematica implementada no backend que reconhece a limitacao da WAN.

---

## Anexo: Guia de Comandos de Rede (Linux)
Para que a topologia funcione, A equipe  devera rodar os seguintes comandos nos Linux que atuam como R1 e R2 (seja Vagrant ou Notebook fisico). Substitua `ethX` pelo nome correto da placa de rede.na 

### 1. Roteamento e Multicast (R1 e R2)
Para permitir que os roteadores repassem os pacotes de video (IPs `239.x.x.x`):
```bash
# Entrar como root
sudo su

# Habilitar roteamento normal de internet (IPv4 Forwarding)
echo 1 > /proc/sys/net/ipv4/ip_forward

# Habilitar roteamento Multicast no Kernel
echo 1 > /proc/sys/net/ipv4/conf/all/mc_forwarding
```
*Dica: Podera ser necessario instalar o daemon `pimd` ou o `smcroute` para gerenciar a arvore multicast dependendo da distribuicao Linux utilizada.*

### 2. Controle de Banda / QoS (R2 - Interface WAN)
Para esmagar a banda do link simulando o gargalo de 115Kbps exigido pelo professor:
```bash
# Se eth1 for a placa conectada na WAN
sudo tc qdisc add dev eth1 root tbf rate 115200bit burst 10kb latency 50ms
```

### 3. Mascaramento NAT (R1)
Para permitir que a maquina S acesse outras redes escondida atras do R1:
```bash
sudo iptables -t nat -A POSTROUTING -o eth_saida -j MASQUERADE
```

### 4. Servidor DHCP (Exemplo R1 para rede LAN1)
```bash
sudo apt install isc-dhcp-server

# Editar o arquivo /etc/dhcp/dhcpd.conf
subnet 172.16.0.0 netmask 255.255.0.0 {
  range 172.16.0.10 172.16.0.100;
  option routers 172.16.0.254;
}

# Reiniciar o servico
sudo systemctl restart isc-dhcp-server
```

---

## Referencial Teorico

Este projeto foi construido aplicando conceitos fundamentais da literatura classica de Redes de Computadores (ex: Kurose & Ross, Tanenbaum) e normas oficiais (RFCs):

1. **Roteamento Multicast ([RFC 1112](https://datatracker.ietf.org/doc/html/rfc1112) / IGMP):** Utilizado para otimizar o fluxo de video. Diferente do Unicast, o servidor envia apenas um pacote de video para um IP de Classe D (`239.x.x.x`), e a infraestrutura de rede cuida de replicar o pacote apenas para os clientes que assinaram o canal via IGMP.
2. **Traffic Shaping e QoS ([Token Bucket](https://man7.org/linux/man-pages/man8/tc-tbf.8.html)):** Aplicado no gargalo da rede WAN usando a ferramenta `tc` do Linux com o algoritmo matematico TBF (Token Bucket Filter). Ele impoe uma fila rigorosa limitando a vazao exata para 115Kbps.
3. **Transporte de Multimidia ([UDP](https://datatracker.ietf.org/doc/html/rfc768) e [MPEG-TS](https://en.wikipedia.org/wiki/MPEG_transport_stream)):** A transmissao ao vivo prioriza a pontualidade em vez da integridade. Por isso, usa-se UDP ao inves de TCP (evitando engasgos de retransmissao). Para garantir resiliencia contra as perdas no UDP, o video e encapsulado no padrao oficial da TV Digital, o MPEG Transport Stream (MPEG-TS).
4. **Seguranca e Controle de Acesso ([RFC 7519 - JSON Web Token](https://datatracker.ietf.org/doc/html/rfc7519)):** A autenticacao da API implementa estritamente as diretrizes da RFC 7519, utilizando uma representacao compacta e URL-safe para a transferencia de *Claims* (neste projeto, o perfil de rede do usuario: LAN ou WAN). O payload do JWT e protegido por integridade e assinado digitalmente usando a especificacao JWS (JSON Web Signature). Isso garante uma arquitetura *Stateless*, onde o servidor nao precisa onerar o banco de dados para validar sessoes, reduzindo a latencia no controle de acesso aos fluxos de video.
5. **Arquitetura de Proxy Reverso ([Apache mod_proxy](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html)):** O Apache e utilizado no roteador de borda (R1) para interceptar pacotes HTTP e mascarar a topologia real da rede interna (DMZ), protegendo o Servidor Python.

---
Desenvolvido para a disciplina de Fundamentos de Redes de Computadores.
