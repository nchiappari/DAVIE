Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.provider "virtualbox" do |v|
    v.name = "my_vm"
  end

  config.vm.provision :ansible do |ansible|
    ansible.groups = {
      "servers" => ["my_vm"]
    }
    ansible.limit = "all"
    ansible.playbook = "playbook.yaml"
  end

end
