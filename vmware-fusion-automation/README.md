# create vm

1. Hostname of vm decide the role of node.
- Register nodes in config.yaml
- Master nodes: m1,m2,m3.. where `m` is master and `m1` is primary master
- Worker nodes: w1,w2,w3.. where `w` is worker nodes, for categorizing worker nodes, use `-<node_type>`. eg: w1-c1 where `c` is compute node.
Define worker types in `config.yaml`
- LB nodes: `lb<index>`, eg: l1,l2,l3.. where l1 is primary lb
- DNS nodes: `dns` where dns is a sole node
- Other nodes: <vm_hostname>:<ansible_group_name>

# run setup script
```sh
# install nmap
brew install nmap

# install python packages
pip install -r requirements.txt

# get virtual ip address and vm machines descriptions
sudo python 1-collect-vmware-machines.py

# create inventories, variables and other configs
python 2-create-ansible-inventory.py

# start vm (and clean lck files)
python 3-start-vmware-machines.py
```

# execute playbooks
```sh
ansible-playbook -i inventories.yaml -K playbooks/1-pre-installation.yaml
ansible-playbook -i inventories.yaml -K playbooks/2.1-setup-loadbalancer.yaml
ansible-playbook -i inventories.yaml -K playbooks/2.2-setup-dns.yaml
ansible-playbook -i inventories.yaml -K playbooks/2.3-setup-nfs-server.yaml
ansible-playbook -i inventories.yaml -K playbooks/2.4-setup-db.yaml
ansible-playbook -i inventories.yaml -K playbooks/3.1-upload-tokens.yaml
ansible-playbook -i inventories.yaml -K playbooks/3.2-setup-masters.yaml
ansible-playbook -i inventories.yaml -K playbooks/3.3-setup-workers.yaml
ansible-playbook -i inventories.yaml -K --extra-vars "local_kubeconfig_dir=$HOME" playbooks/4-download-kubeconfig.yaml
ansible-playbook -i inventories.yaml -K playbooks/5-uninstall-cluster.yaml
```

# clean up lck files
```sh
for f in $(find . -mindepth 1 -maxdepth 1 -type d); do rm -r  "$f/*.lck" || true; done
```
