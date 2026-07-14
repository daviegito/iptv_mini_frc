Vagrant.configure("2") do |config|
  config.vm.box = "generic/ubuntu2204"

  # Força aceleração de hardware (KVM) e reduz drasticamente o consumo de RAM/CPU
  config.vm.provider :libvirt do |libvirt|
    libvirt.driver = "kvm"
    libvirt.memory = 512
    libvirt.cpus = 1
  end

  # Roteador 1 (R1)
  config.vm.define "r1" do |r1|
    r1.vm.hostname = "r1"
    r1.vm.network "private_network", ip: "172.16.0.254", libvirt__network_name: "lan1", libvirt__dhcp_enabled: false
    r1.vm.network "private_network", ip: "10.0.0.254", libvirt__network_name: "wan", libvirt__dhcp_enabled: false
  end

  # Roteador 2 (R2)
  config.vm.define "r2" do |r2|
    r2.vm.hostname = "r2"
    r2.vm.network "private_network", ip: "10.0.0.253", libvirt__network_name: "wan", libvirt__dhcp_enabled: false
    r2.vm.network "private_network", ip: "192.168.0.254", libvirt__network_name: "lan2", libvirt__dhcp_enabled: false
  end

  # Servidor Multimídia e Backend (S)
  config.vm.define "s" do |s|
    s.vm.hostname = "s"
    s.vm.network "private_network", ip: "172.16.0.2", libvirt__network_name: "lan1", libvirt__dhcp_enabled: false
  end

  # Cliente X (Na rede lenta LAN2)
  config.vm.define "x" do |x|
    x.vm.hostname = "x"
    x.vm.network "private_network", ip: "192.168.0.10", libvirt__network_name: "lan2", libvirt__dhcp_enabled: false
  end

  # Cliente Y (Na rede lenta LAN2)
  config.vm.define "y" do |y|
    y.vm.hostname = "y"
    y.vm.network "private_network", ip: "192.168.0.11", libvirt__network_name: "lan2", libvirt__dhcp_enabled: false
  end
end
