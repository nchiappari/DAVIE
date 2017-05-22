
Vagrant.configure("2") do |config|
  # Configure the virtualization provider
  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.memory = "1024"
  end

  # Configure a VM for MediFor
  config.vm.define "medifor" do |medifor|
    medifor.vm.box = "ubuntu/xenial64"
  end

  # Configure provisioner
  config.vm.provision "ansible" do |ansible|
    ansible.groups = {
      "servers" => ["medifor"]
    }
    ansible.playbook = "provisioning/playbook.yaml"
  end
end
