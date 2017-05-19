Vagrant.configure("2") do |config|
  config.vm.box = "hashicorp/precise64"

  config.vm.provision :ansible do |ansible|
    ansible.inventory_path = "hosts"
    ansible.limit = "all"
    ansible.playbook = "playbook.yaml"
  end

end
