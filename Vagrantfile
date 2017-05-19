Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.provision :ansible do |ansible|
    ansible.groups = {
      "servers" => ["127.0.0.1:2222"]
    }
    ansible.limit = "all"
    ansible.playbook = "playbook.yaml"
  end

end
