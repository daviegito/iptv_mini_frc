# Mini-IPTV Multicast com Controle de Banda (FRC)

Projeto universitário focado na construção de uma arquitetura completa de redes de computadores, unindo infraestrutura (Roteamento, Multicast, QoS/TC, Proxy Reverso) e desenvolvimento de software (API RESTful, JWT, Web Frontend).

## Arquitetura do Sistema

O projeto é dividido em três grandes blocos:
1. **Frontend (`/frontend`)**: Interface web construída em HTML5, CSS3 (Glassmorphism) e Vanilla Javascript. Responsável por consumir a API e disparar o VLC via download dinâmico de playlists `.m3u`.
2. **Backend (`/backend`)**: API desenvolvida em Python (FastAPI). Responsável pela autenticação segura de usuários (JWT), banco de dados (SQLite) e orquestração do FFmpeg para transmissão de streams de vídeo UDP (Multicast).
3. **Infraestrutura (`/infra` e `Vagrantfile`)**: Topologia de rede simulada com máquinas virtuais gerenciadas pelo Vagrant (hypervisor Libvirt/KVM). Contém a planta dos roteadores, clientes e configurações do Apache.

## Como Executar no Dia da Apresentacao

Siga os passos rigorosamente nesta ordem para garantir que a rede e a aplicação funcionem em harmonia.

### Passo 1: Subir a Infraestrutura Física (VMs)
No terminal do seu computador (hospedeiro), crie as máquinas:
```bash
vagrant up --no-parallel
```
*(Nota: O uso do `--no-parallel` evita gargalos de timeout no Vagrant/Libvirt).*

### Passo 2: Configurar o Roteamento e QoS (R1 e R2)
Acesse os roteadores via `vagrant ssh r1` e `vagrant ssh r2`.
A equipe de redes deve realizar as seguintes configurações manuais (conforme o PDF):
- **DHCP**: Instalar o `isc-dhcp-server` para fornecer IPs para os clientes.
- **Roteamento Multicast**: Habilitar IGMP/PIM para que os pacotes `239.x.x.x` atravessem a rede.
- **Controle de Banda (Traffic Control)**: Aplicar as regras do `tc` no R2 para limitar a interface da rede WAN (clientes X e Y) em **115200 bps**.

### Passo 3: Configurar o Proxy Reverso (Apache no R1)
O Roteador 1 atua como o portão de entrada para o servidor web.
```bash
vagrant ssh r1
sudo apt update && sudo apt install -y apache2
sudo a2enmod proxy proxy_http
sudo cp /vagrant/infra/apache_proxy.conf /etc/apache2/sites-available/iptv.conf
sudo mkdir -p /var/www/html/iptv
sudo cp -r /vagrant/frontend/* /var/www/html/iptv/
sudo a2ensite iptv.conf && sudo a2dissite 000-default.conf
sudo systemctl reload apache2
```

### Passo 4: Ligar o Servidor Backend (S)
Acesse a máquina servidora que está conectada na LAN1:
```bash
vagrant ssh s
sudo apt update && sudo apt install -y python3-venv python3-pip ffmpeg
cd /vagrant/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Passo 5: Teste Final (Clientes X, Y, Z ou W)
1. Acesse o cliente (ex: `vagrant ssh x` ou via ambiente gráfico).
2. Abra o navegador web e digite o IP do Roteador **R1** (A porta 80 do R1 redirecionará para o Frontend, que por sua vez comunicará via Proxy com o Backend na máquina S).
3. Faça login com o usuário apropriado:
   - Clientes LAN: `hostz` ou `hostw` (Acesso total de banda).
   - Clientes WAN: `hostx` ou `hosty` (Gatilho da regra de limitação 115K e compressão para 80kbps pelo FFmpeg).
4. Clique em "Assistir". O VLC será aberto automaticamente lendo o IP de Multicast da rede correta!

---
Desenvolvido para a disciplina de Fundamentos de Redes de Computadores.
